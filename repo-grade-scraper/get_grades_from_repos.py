import argparse
import json
import os
import subprocess
import re
import csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from enum import Enum
from datetime import datetime


class ModuleType(Enum):
    GROUP = "group"
    INDIVIDUAL = "individual"


class Error(Enum):
    NO_README = "README.md not found"
    NO_GRADE = "Grade not found"
    NO_BRANCH = "Grading branch not found"
    NO_STUDENT_ID = "Student ID not found"
    CLONE_FAILED = "Failed to clone repository"


error_log_lock = Lock()
run_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
error_log_path = f"./error_log_{run_datetime}.csv"


def get_module_type(args):
    """Get the module type from the user."""
    module_type = args.module_type
    if module_type not in {ModuleType.GROUP.value, ModuleType.INDIVIDUAL.value}:
        print(
            f"You must specify either 'group' or 'individual' module type. Received: {module_type}"
        )
        exit()
    # map the input to the Enum value
    module_type = ModuleType(module_type)
    print(f"Processing {module_type.value} repositories.")
    return module_type


def write_to_error_log(problematic_repo_url: str, error_type: Error):
    """Write problematic repo and error message to a csv file."""

    with error_log_lock:
        os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
        try:
            header_needed = (
                not os.path.exists(error_log_path)
                or os.path.getsize(error_log_path) == 0
            )
            with open(
                error_log_path, mode="a", newline="", encoding="utf-8"
            ) as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["REPO_URL", "ERROR"])
                if header_needed:
                    writer.writeheader()
                writer.writerow(
                    {"REPO_URL": problematic_repo_url, "ERROR": error_type.value}
                )

        except IOError as e:
            print(f"An IO error occurred: {e}")


def get_assignment_repos(template_repo_name, github_org):
    response = subprocess.run(
        ["gh", "api", f"repos/{github_org}/{template_repo_name}/forks", "--paginate"],
        capture_output=True,
        text=True,
    )

    response_json = json.loads(response.stdout)

    if type(response_json) != list:
        if response_json["message"] == "Not Found":
            print("Repo not found")
            return []

    repo_urls = []

    for repo in response_json:
        print(repo["html_url"])
        repo_urls.append(repo["html_url"])

    return repo_urls


def confirm_repos_are_ok(repos):
    """Prompt user confirmation for the parsed repository names."""
    print(repos)
    print(f"Found {len(repos)} repositories.")
    confirmation = (
        input("Do these look like the correct repos? (yes/no): ").strip().lower()
    )
    if confirmation not in {"yes", "y"}:
        print(f"Exiting: Confirmation failed ({confirmation}).")
        exit()


def find_grade_in_readme(readme_content, repo_url, module_type: ModuleType):
    """Extract grade details and student ID from the README content."""
    total_earned, total_possible, student_ids = (
        None,
        None,
        set(),
    )  # Set to prevent duplicate student_id entries
    lines = readme_content.splitlines()
    for i, line in enumerate(lines):
        if total_earned is None and "Total Earned" in line and i + 2 < len(lines):
            data_line = lines[i + 2].split("|")
            if len(data_line) >= 3:
                total_earned = data_line[1].strip()
                total_possible = data_line[2].strip()

        matches = re.findall(r"\b\d{6}\b", line)
        student_ids.update(matches)

        if total_earned and total_possible and student_ids:
            break

    if not total_earned:
        write_to_error_log(repo_url, Error.NO_GRADE)
    if len(student_ids) == 0:
        write_to_error_log(repo_url, Error.NO_STUDENT_ID)

    return total_earned, total_possible, student_ids


def process_single_repo(repo_url, parsed_grades, module_type: ModuleType):
    """Process a single repository to parse grades."""
    repo_path = f"./temporary-repo-directory/{repo_url.split('/')[-1]}"

    # Clone the repository
    subprocess.run(
        ["git", "clone", repo_url, repo_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not os.path.exists(repo_path):
        print(f"[ERROR] Failed to clone {repo_url}. Skipping {repo_url}.")
        write_to_error_log(repo_url, Error.CLONE_FAILED)
        return

    # Checkout the grading branch
    branch_name = "grading"
    result = subprocess.run(
        ["git", "-C", repo_path, "checkout", branch_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        print(f"[ERROR] Grading branch does not exist for {repo_url}.")
        write_to_error_log(repo_url, Error.NO_BRANCH)
        subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL)
        return

    # Parse README content
    readme_path = os.path.join(repo_path, "README.md")
    try:
        with open(readme_path, "r") as readme_file:
            readme_content = readme_file.read()

        total_earned, total_possible, student_ids = find_grade_in_readme(
            readme_content, repo_url, module_type
        )
        if total_earned and total_possible and len(student_ids) > 0:
            for student_id in student_ids:
                parsed_grades.append(
                    {
                        "STUDENT_ID": student_id,
                        "GRADE": total_earned,
                        "REPO_URL": repo_url,
                    }
                )
            print(
                f"[SUCCESS] Parsed grade: {total_earned}/{total_possible} for {repo_url}."
            )
        else:
            print(f"[ERROR] Incomplete grade data for {repo_url}.")
            # no need to write to error log here, it's already done in find_grade_in_readme
    except FileNotFoundError:
        print(f"[ERROR] README.md not found in {repo_url}.")
        write_to_error_log(repo_url, Error.NO_README)

    # Clean up the cloned repository
    subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL)


def parallelize_grade_parsing(repo_urls, module_type):
    """Parse grades from repositories in parallel."""
    parsed_grades = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_single_repo, repo, parsed_grades, module_type)
            for repo in repo_urls
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")

    return parsed_grades


def write_to_csv(file_path, data):
    """Write parsed grades to a CSV file."""

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=["STUDENT_ID", "GRADE", "REPO_URL"]
        )
        writer.writeheader()
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(
        description="Parse grades from GitHub repositories."
    )
    parser.add_argument("module_number", help="Module number (e.g., '1', '2', etc.).")
    parser.add_argument(
        "module_type", help="Type of repositories: 'group' or 'individual'."
    )
    parser.add_argument("org_name", help="GitHub organization name.")
    parser.add_argument(
        "assignment_repo_template", help="Template repo name for assignment."
    )

    args = parser.parse_args()

    module_number = args.module_number
    module_type = get_module_type(args)
    org_name = args.org_name

    print(f"Processing module {module_number} ({module_type}) repositories.")
    repo_urls = get_assignment_repos(args.assignment_repo_template, org_name)
    confirm_repos_are_ok(repo_urls)

    base_url = f"https://github.com/{org_name}/"
    parsed_grades = parallelize_grade_parsing(repo_urls, module_type)

    output_path = f"./results/module-{module_number}-{module_type.value}.csv"
    write_to_csv(output_path, parsed_grades)

    def count_errors():
        error_count = 0
        lines_to_skip = 1  # Skip the header line
        if not os.path.exists(error_log_path):
            return error_count
        with open(error_log_path, "r") as infile:
            for i, line in enumerate(infile):
                if i < lines_to_skip:
                    continue
                error_count += 1
        print(f"  Failed to process: {error_count}")
        return error_count

    total_count = len(repo_urls)
    success_count = total_count - count_errors()
    print(f"\nProcessing complete:")
    print(f"  Total student grades: {total_count}")
    print(f"  Successfully processed: {success_count}")
    print(f"  Failed to process: {total_count - success_count}")
    print(f"  Success rate: {success_count / total_count:.2%}")


if __name__ == "__main__":
    main()
