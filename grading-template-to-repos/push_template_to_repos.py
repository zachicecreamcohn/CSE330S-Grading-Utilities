import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor


def parse_repo_names_from_txt(module_number, group_or_individual):
    """Parse repository names from the given text file."""
    file_type = "individual" if group_or_individual == "individual" else "group"
    repo_mapping_file_path = f"./text-grader-mappings/module-{module_number}-{file_type}.txt"

    repo_names = []
    try:
        with open(repo_mapping_file_path, 'r') as infile:
            for line in infile:
                parts = line.strip().split(':')
                if len(parts) > 2:
                    repo_names.append(parts[1])  # Extract the repo name
                else:
                    print(f"[WARNING] Skipping malformed line: {line}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {repo_mapping_file_path}")
        exit(1)

    return repo_names


def confirm_repo_names_are_ok(repo_names):
    """Prompt user confirmation for the parsed repository names."""
    print(repo_names)
    confirmation = input("Do these look like the correct repos? (yes/no): ").strip().lower()
    if confirmation not in {"yes", "y"}:
        print(f"Exiting: Confirmation failed ({confirmation}).")
        exit()


def get_markdown_content_to_push_to_readme(module_number, group_or_individual):
    """Retrieve markdown content to push into README files."""
    file_type = "individual" if group_or_individual == "individual" else "group"
    markdown_template_file_path = f"./rubrics/module-{module_number}/{file_type}.md"

    template_text = "# Grading\n\n"
    try:
        with open(markdown_template_file_path, 'r') as infile:
            template_text += "".join(line.strip() + "\n" for line in infile)
    except FileNotFoundError:
        print(f"[ERROR] Markdown template file not found: {markdown_template_file_path}")
        exit(1)

    return template_text


def process_single_repo(repo, base_url, content_to_push):
    """Process a single repository by cloning, updating, and pushing changes."""
    full_repo_url = f"{base_url}{repo}"
    repo_path = f"./temporary-repo-directory/{repo}"

    # Clone the repository
    clone_result = subprocess.run(
        ["git", "clone", full_repo_url, repo_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    if not os.path.exists(repo_path):
        print(f"[ERROR] Failed to clone {repo}. Skipping {full_repo_url}...")
        return

    branch_name = "grading"

    # Check out or create the grading branch
    result = subprocess.run(
        ["git", "-C", repo_path, "checkout", branch_name],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        subprocess.run(
            ["git", "-C", repo_path, "checkout", "-b", branch_name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    # Add content to README.md
    readme_path = os.path.join(repo_path, "README.md")
    try:
        with open(readme_path, "a") as readme_file:
            readme_file.write("\n" + content_to_push)
    except Exception as e:
        print(f"[ERROR] Failed to write to README.md for {repo}: {e}")
        return

    # Commit and push changes
    subprocess.run(["git", "-C", repo_path, "add", "README.md"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "-C", repo_path, "commit", "-m", "Add grading template to grading branch"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    push_result = subprocess.run(
        ["git", "-C", repo_path, "push", "-u", "origin", branch_name],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        text=True
    )

    # Clean up the cloned repository
    subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL)

    if push_result.returncode == 0:
        print(f"[SUCCESS] Grading template pushed to {full_repo_url} on branch: {branch_name}")
    else:
        error_message = push_result.stderr.strip()
        print(f"[FAILURE] Failed to push grading template to {full_repo_url} on branch: {branch_name}. Error: {error_message}")


def push_template_to_repos_on_grading_branch(repo_names, org_name, content_to_push):
    """Push templates to all repositories in parallel."""
    base_url = f"https://github.com/{org_name}/"
    with ThreadPoolExecutor() as executor:
        executor.map(lambda repo: process_single_repo(repo, base_url, content_to_push), repo_names)


def main():
    parser = argparse.ArgumentParser(description="Push grading templates to GitHub repositories.")
    parser.add_argument('module_number', help="Module number of the text file (e.g., '1', '2').")
    parser.add_argument('group_or_individual', help="Repository type: 'group' or 'individual'.")
    parser.add_argument('org_name', help="GitHub organization name.")
    args = parser.parse_args()

    module_number = args.module_number
    group_or_individual = args.group_or_individual
    org_name = args.org_name

    print(f"Preparing to push grading templates for module {module_number} ({group_or_individual}) repositories.")
    repo_names = parse_repo_names_from_txt(module_number, group_or_individual)
    confirm_repo_names_are_ok(repo_names)

    content_to_push = get_markdown_content_to_push_to_readme(module_number, group_or_individual)
    push_template_to_repos_on_grading_branch(repo_names, org_name, content_to_push)


if __name__ == "__main__":
    main()
