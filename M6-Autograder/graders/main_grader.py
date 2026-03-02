import os
import re
import subprocess
from graders.base_grader import BaseGrader
from graders.baseball_grader import BaseballGrader
from graders.regex_2_grader import Regex2Grader
from graders.regex_3_grader import Regex3Grader
from graders.regex_1_grader import Regex1Grader


class MainGrader(BaseGrader):
    def __init__(self, repo_link, repo_location=None):
        super().__init__()
        self.points_possible = 50
        self.repo_link = repo_link
        self.regex1_path = ""
        self.regex2_path = ""
        self.regex3_path = ""
        self.baseball_path = ""
        self.repo_dir = ""
        if not repo_location:
            self.clone_repo()
        else:
            self.repo_dir = repo_location

        self.checkout_grading()

    def record_problematic_repo(self, error_message):
        if not os.path.exists("m4_autograder_errors.csv"):
            with open("m4_autograder_errors.csv", "w") as file:
                file.write("Repo Link, Error Message\n")

        with open("m4_autograder_errors.csv", "a") as file:
            file.write(f"{self.repo_link}, {error_message}\n")

        raise Exception(error_message)

    def clone_repo(self):
        self.repo_dir = self.repo_link.split("/")[-1]
        subprocess.run(["git", "clone", self.repo_link, self.repo_dir])

    def checkout_grading(self):
        subprocess.run(
            ["git", "-C", self.repo_dir, "checkout", "-b", "grading"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.regex1_path = self.get_regex_path(1)
        self.regex2_path = self.get_regex_path(2)
        self.regex3_path = self.get_regex_path(3)
        self.baseball_path = self.get_baseball_path()

    def recursive_search(self, file_pattern):

        pattern = re.compile(file_pattern)
        for root, _, files in os.walk(self.repo_dir):
            for file in files:
                if pattern.search(file):
                    return os.path.join(root, file)
        return ""

    def get_regex_path(self, regex_num):
        pattern = "^regex" + str(regex_num) + r"\.txt$"
        path = self.recursive_search(pattern)
        if not path:
            self.record_problematic_repo(
                f"Couldn't find regex{regex_num}.txt in the repo."
            )
        return path

    def get_baseball_path(self):
        path = self.recursive_search(r"^baseball\.py$")
        if not path:
            path = self.recursive_search(r".*\.py$")

        if not path:
            self.record_problematic_repo(
                "Couldn't find baseball.py or any python file in the repo."
            )

        return path

    def grade(self):
        self.regex1_grader = Regex1Grader(self.regex1_path)
        self.regex2_grader = Regex2Grader(self.regex2_path)
        self.regex3_grader = Regex3Grader(self.regex3_path)
        self.baseball_grader = BaseballGrader(self.baseball_path)

        self.regex1_grader.grade()
        self.regex2_grader.grade()
        self.regex3_grader.grade()
        self.baseball_grader.grade()

        self.points_deducted += (
            self.regex1_grader.points_deducted
            + self.regex2_grader.points_deducted
            + self.regex3_grader.points_deducted
            + self.baseball_grader.points_deducted
        )

    def provide_feedback(self):
        markdown = f"""
# Grading

## Regex
| Title  | Possible Points | Points Earned | Feedback |
| ------ | --------------- | ------------- | ----------- |
| Regex1 |5|{self.regex1_grader.compute_points()}|{self.regex1_grader.get_feedback()}|
| Regex2 |5|{self.regex2_grader.compute_points()}|{self.regex2_grader.get_feedback()}|
| Regex3 |5|{self.regex3_grader.compute_points()}|{self.regex3_grader.get_feedback()}|

## Baseball
| Title                     | Possible Points | Points Earned | Feedback |
| ------------------------- | --------------- | ------------- | ----------- |
| File called baseball.py   | 8               | 8             |             |
| Uses Regex to parse input | 8               |{self.baseball_grader.uses_regex_grader.compute_points()}|{self.baseball_grader.uses_regex_grader.get_feedback()}|
| Usage Message             | 4               |{self.baseball_grader.usage_message_grader.compute_points()}|{self.baseball_grader.usage_message_grader.get_feedback()}|
| Correct Output            | 15              |{self.baseball_grader.baseball_output_grader.compute_points()}|{self.baseball_grader.baseball_output_grader.get_feedback()}|

## Total Points

{self.compute_points()} / {self.points_possible}
        """
        with open(f"{self.repo_dir}/README.md", "a") as file:
            file.write(markdown)

    def get_student_id(self):
        with open(f"{self.repo_dir}/README.md", "r") as file:
            content = file.read()
            match = re.search(r"\d{6}", content)
            if match:
                return match.group(0)
            return "000000"

    def record_grade(self):
        if not os.path.exists("m4_autograder_results.csv"):
            with open("m4_autograder_results.csv", "w") as file:
                file.write("STUDENT_ID,GRADE,REPO_LINK\n")
        with open("m4_autograder_results.csv", "a") as file:
            file.write(
                f"{self.get_student_id()},{self.compute_points()},{self.repo_link}\n"
            )

    def push_and_cleanup(self):
        # push the changes to the repo
        subprocess.run(["git", "-C", self.repo_dir, "add", "."])
        subprocess.run(
            ["git", "-C", self.repo_dir, "commit", "-m", "Grading completed."]
        )
        subprocess.run(["git", "-C", self.repo_dir, "push", "-u", "origin", "grading"])

    def main(self):
        self.grade()
        self.provide_feedback()
        self.record_grade()
        self.push_and_cleanup()
