import argparse
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
        "repo_dir", help="directory to clone repos into", default="m4_grading_repos"
    )
    return parser.parse_args()


def get_repo_URLs(repos_txt, github_org):
    with open(repos_txt, "r") as file:
        return [
            f"https://github.com/{github_org}/{repo_name}.git"
            for repo_name in file.read().split("\n")
            if repo_name
        ]


def main():
    args = setup()
    repo_URLs = get_repo_URLs(args.repos_txt, args.github_org)
    for repo_URL in repo_URLs:
        grader = MainGrader(repo_URL)
        grader.main()


if __name__ == "__main__":
    main()
