import argparse
import json
import subprocess
import os
from graders.main_grader import MainGrader


def setup():
    parser = argparse.ArgumentParser(description="Module 4 Autograder.")
    parser.add_argument(
        "repos_txt", help="txt file containing repo names, one per line"
    )
    parser.add_argument(
        "github_org", help="github organization name (e.g., 'cse330-spring-2025')"
    )
    parser.add_argument(
        "assignment_repo_template", help="Template repo name for assignment."
    )
    return parser.parse_args()


def remove_old_files():
    if os.path.exists("m4_autograder_results.csv"):
        os.remove("m4_autograder_results.csv")
    if os.path.exists("m4_autograder_errors.csv"):
        os.remove("m4_autograder_errors.csv")


def write_to_error_log(repo_link, error_message):
    if not os.path.exists("m4_autograder_errors.csv"):
        with open("m4_autograder_errors.csv", "w") as file:
            file.write("Repo Link, Error Message\n")

    with open("m4_autograder_errors.csv", "a") as file:
        file.write(f"{repo_link}, {error_message}\n")


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


def main():
    args = setup()
    remove_old_files()
    repo_URLs = get_assignment_repos(args.assignment_repo_template, args.github_org)
    for repo_URL in repo_URLs:
        try:
            grader = MainGrader(repo_URL)
            grader.main()
        except Exception as e:
            write_to_error_log(repo_URL, str(e))


if __name__ == "__main__":
    main()
