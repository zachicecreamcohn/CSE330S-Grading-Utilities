import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor


def parse_repo_names_from_txt(module_number, group_or_individual):
    if group_or_individual == "individual":
        repo_mapping_file_path = f"./text-grader-mappings/module-{module_number}-individual.txt"
    else:
        repo_mapping_file_path = f"./text-grader-mappings/module-{module_number}-group.txt"

    data = []
    with open(repo_mapping_file_path, 'r') as infile:
        for line in infile:
            parts = line.strip().split(':')
            if len(parts) > 2:
                repo_name = parts[1]  # We only care about the repo_name.
                data.append(repo_name)
            else:
                print(f"Skipping malformed line: {line}")
    return data


def confirm_repo_names_are_ok(repo_names):
    print(repo_names)
    confirmation = input("Do these look like the correct repos? (yes/no): ").strip().lower()

    if confirmation not in {"yes", "y"}:
        print(f"Ok... Exiting program because you said {confirmation}")
        exit()


def get_markdown_content_to_push_to_readme(module_number, group_or_individual):
    if group_or_individual == "individual":
        markdown_template_file_path = f"./rubrics/module-{module_number}/individual.md"
    else:
        markdown_template_file_path = f"./rubrics/module-{module_number}/group.md"

    template_text = "# Grading\n\n"
    with open(markdown_template_file_path, 'r') as infile:
        for line in infile:
            template_text += f"{line.strip()}\n"
    return template_text


def process_single_repo(repo, base_url, content_to_push):
    full_repo_url = f"{base_url}{repo}"
    repo_path = f"./temporary-repo-directory/{repo}"

    # Clone the repository
    subprocess.run(["git", "clone", full_repo_url, repo_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Check if cloning succeeded
    if not os.path.exists(repo_path):
        print(f"Failed to clone {repo}. Skipping {full_repo_url}...")
        return

    branch_name = "grading"

    # Check if the grading branch exists, and create it if it doesn't
    result = subprocess.run(
        ["git", "-C", repo_path, "checkout", branch_name],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        subprocess.run(["git", "-C", repo_path, "checkout", "-b", branch_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Add content to README.md
    readme_path = os.path.join(repo_path, "README.md")
    with open(readme_path, "a") as readme_file:
        readme_file.write("\n" + content_to_push)

    # Commit and push changes
    subprocess.run(["git", "-C", repo_path, "add", "README.md"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "-C", repo_path, "commit", "-m", "Add grading template to grading branch"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Attempt to push the changes
    result = subprocess.run(
        ["git", "-C", repo_path, "push", "-u", "origin", branch_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    # Clean up the cloned repository
    subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL)

    if result.returncode == 0:
        print(f"[SUCCESS]: Grading Template has been pushed to {full_repo_url} on branch: {branch_name}")
    else:
        error_message = result.stderr.strip()
        print(f"[FAILURE]: Grading Template failed to push to {full_repo_url} on branch: {branch_name}. Error: {error_message}")


def push_template_to_repos_on_grading_branch(repo_names, org_name, content_to_push):
    base_url = f"https://github.com/{org_name}/"
    # For parallelization - Thanks Professor Cosgrove :) & https://www.geeksforgeeks.org/how-to-use-threadpoolexecutor-in-python3/
    with ThreadPoolExecutor() as exe:
        exe.map(lambda repo: process_single_repo(repo, base_url, content_to_push), repo_names)


def main():
    parser = argparse.ArgumentParser(description='Convert a text file to JSON format with keys "Module" and "TA Username".')
    parser.add_argument('module_number', help='Module number of the text file (as received from Prof. Sproull). The file must be named "module-<module_number>-<group_or_individual>.txt"')
    parser.add_argument('group_or_individual', help='Repository type of the text file (as received from Prof. Sproull). The file must be named "module-<module_number>-<group_or_individual>.txt"')
    parser.add_argument('org_name', help='The organization name for repos.')
    args = parser.parse_args()
    MODULE_NUMBER = args.module_number
    GROUP_OR_INDIVIDUAL = args.group_or_individual
    ORG_NAME = args.org_name
    repo_names = parse_repo_names_from_txt(MODULE_NUMBER, GROUP_OR_INDIVIDUAL)
    confirm_repo_names_are_ok(repo_names)  # Will exit if you deem not
    markdown_grading_template_content = get_markdown_content_to_push_to_readme(MODULE_NUMBER, GROUP_OR_INDIVIDUAL)
    push_template_to_repos_on_grading_branch(repo_names, ORG_NAME, markdown_grading_template_content)



if __name__ == "__main__":
    main()
