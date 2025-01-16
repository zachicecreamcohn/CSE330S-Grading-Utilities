import argparse
import os
import subprocess
import re
import csv
from concurrent.futures import ThreadPoolExecutor


def parse_repo_names_from_txt(module_number, group_or_individual):
    """Parse repository names from the specified text file."""
    file_type = "individual" if group_or_individual == "individual" else "group"
    repo_mapping_file_path = f"./text-grader-mappings/module-{module_number}-{file_type}.txt"

    repo_names = []
    with open(repo_mapping_file_path, 'r') as infile:
        for line in infile:
            parts = line.strip().split(':')
            if len(parts) > 2:
                repo_names.append(parts[1])  # Extract repo name
            else:
                print(f"Skipping malformed line: {line}")

    return repo_names


def confirm_repo_names_are_ok(repo_names):
    """Prompt user confirmation for the parsed repository names."""
    print(repo_names)
    confirmation = input("Do these look like the correct repos? (yes/no): ").strip().lower()
    if confirmation not in {"yes", "y"}:
        print(f"Exiting: Confirmation failed ({confirmation}).")
        exit()


def find_grade_in_readme(readme_content):
    """Extract grade details and student ID from the README content."""
    total_earned, total_possible, student_id = None, None, None
    lines = readme_content.splitlines()

    for i, line in enumerate(lines):
        if total_earned is None and "Total Earned" in line and i + 2 < len(lines):
            data_line = lines[i + 2].split('|')
            if len(data_line) >= 3:
                total_earned = data_line[1].strip()
                total_possible = data_line[2].strip()

        if student_id is None:
            match = re.search(r"\b\d{6}\b", line)
            if match:
                student_id = match.group()

        if total_earned and total_possible and student_id:
            break

    return total_earned, total_possible, student_id


def process_single_repo(repo, base_url, parsed_grades):
    """Process a single repository to parse grades."""
    full_repo_url = f"{base_url}{repo}"
    repo_path = f"./temporary-repo-directory/{repo}"

    # Clone the repository
    subprocess.run(["git", "clone", full_repo_url, repo_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(repo_path):
        print(f"[ERROR] Failed to clone {repo}. Skipping {full_repo_url}.")
        return

    # Checkout the grading branch
    branch_name = "grading"
    result = subprocess.run(["git", "-C", repo_path, "checkout", branch_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        print(f"[ERROR] Grading branch does not exist for {full_repo_url}.")
        subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL)
        return

    # Parse README content
    readme_path = os.path.join(repo_path, "README.md")
    try:
        with open(readme_path, "r") as readme_file:
            readme_content = readme_file.read()

        total_earned, total_possible, student_id = find_grade_in_readme(readme_content)
        if total_earned and total_possible and student_id:
            parsed_grades.append({"STUDENT_ID": student_id, "GRADE": total_earned})
            print(f"[SUCCESS] Parsed grade: {total_earned}/{total_possible} for {full_repo_url}.")
        else:
            print(f"[ERROR] Incomplete grade data for {full_repo_url}.")
    except FileNotFoundError:
        print(f"[ERROR] README.md not found in {full_repo_url}.")

    # Clean up the cloned repository
    subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL)


def parallelize_grade_parsing(repo_names, base_url):
    """Parse grades from repositories in parallel."""
    parsed_grades = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_repo, repo, base_url, parsed_grades) for repo in repo_names]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")

    return parsed_grades


def write_to_csv(file_path, data, headers):
    """Write parsed grades to a CSV file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(description="Parse grades from GitHub repositories.")
    parser.add_argument('module_number', help="Module number (e.g., '1', '2', etc.).")
    parser.add_argument('group_or_individual', help="Type of repositories: 'group' or 'individual'.")
    parser.add_argument('org_name', help="GitHub organization name.")
    args = parser.parse_args()

    module_number = args.module_number
    group_or_individual = args.group_or_individual
    org_name = args.org_name

    print(f"Processing module {module_number} ({group_or_individual}) repositories.")
    repo_names = parse_repo_names_from_txt(module_number, group_or_individual)
    confirm_repo_names_are_ok(repo_names)

    base_url = f"https://github.com/{org_name}/"
    parsed_grades = parallelize_grade_parsing(repo_names, base_url)

    output_path = f"./results/module-{module_number}-{group_or_individual}.csv"
    write_to_csv(output_path, parsed_grades, ["STUDENT_ID", "GRADE"])

    success_count = len(parsed_grades)
    total_count = len(repo_names)
    print(f"\nProcessing complete:")
    print(f"  Total repos: {total_count}")
    print(f"  Successfully processed: {success_count}")
    print(f"  Failed to process: {total_count - success_count}")
    print(f"  Success rate: {success_count / total_count:.2%}")


if __name__ == "__main__":
    main()
