# a class to handle a single student's grade
import os
import re
from github import Github


class Student:

    def __init__(self, github_conn, repo, repos_destination: str):
        self.repo = repo
        self.g = github_conn
        self.repos_destination = repos_destination

        self.student_ID = None  # will be set later in find_student_id()
        self.grade = None  # will be set later in find_grade()

    def clone_repo(self):
        if not os.path.exists(self.repos_destination):
            os.mkdir(self.repos_destination)

        if os.path.exists(os.path.join(self.repos_destination, self.repo.name)):
            os.system("git -C {} pull".format(os.path.join(self.repos_destination, self.repo.name)))
        else:
            os.system(f"git clone {self.repo.clone_url} {self.repos_destination}"
                      f"/{self.repo.name}")

    def get_grade(self):
        README_path = None
        # find a grade in the repo
        #  Look in grading branch

        # confirm first that there is a grading branch
        try:
            self.repo.get_branch("grading")
        except Exception as e:
            print(f"Error: {e}")
            return None

        # checkout grading branch
        os.system(f"git -C {os.path.join(self.repos_destination, self.repo.name)} checkout grading")

        # now, use regex to find the grade in README.md
        # find a file called README in the repo (recursively)
        for root, dirs, files in os.walk(os.path.join(self.repos_destination, self.repo.name)):
            if "README.md" in files:
                README_path = os.path.join(root, "README.md")
                break

        if not README_path:
            return None

        with open(README_path) as f:
            readme = f.read()

        regex = r"(\d{1,2})\s?\/\s?(\d{1,2})"
        regex = re.compile(regex)
        match = regex.search(readme)

        if match:
            self.grade = match.group(1)
        else:
            self.grade = None

        return self.grade

    def find_student_id(self):
        README_path = None
        # find the student ID in the repo.
        #  Look in the master branch

        # no need to confirm that there is a master branch, because there must be one.

        # checkout master branch
        os.system(f"git -C {os.path.join(self.repos_destination, self.repo.name)} checkout master")

        # find a file called README in the repo (recursively)
        for root, dirs, files in os.walk(os.path.join(self.repos_destination, self.repo.name)):
            if "README.md" in files:
                README_path = os.path.join(root, "README.md")
                break

        if not README_path:
            return None

        with open(README_path) as f:
            readme = f.read()

        regex = r"(\d{6})"
        regex = re.compile(regex)
        match = regex.findall(readme)

        if match:
            # get the last match
            self.student_ID = match[-1]

        else:
            self.student_ID = None

        return self.student_ID
