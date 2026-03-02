import subprocess
import re
import os
from graders.base_grader import BaseGrader
from ollama import chat
from ollama import ChatResponse


class BaseballGrader(BaseGrader):
    def __init__(self, input_file_path):
        super().__init__(input_file_path)

        self.points_possible = 35
        self.uses_regex_grader = self.UsesRegexGrader(input_file_path)
        self.usage_message_grader = self.UsageMessageGrader(input_file_path)
        self.baseball_output_grader = self.BaseballOutputGrader(input_file_path)

    class UsesRegexGrader(BaseGrader):
        def __init__(self, input_file_path):
            super().__init__(input_file_path)
            self.points_possible = 8
            self.baseball_file_contents = []
            self.load_baseball_file_content()

        def load_baseball_file_content(self):
            with open(self.input_file_path, "r") as file:
                self.baseball_file_contents = file.read().splitlines()

        def check_if_re_is_used(self):
            # NOTE: This is called within check_if_string_methods_are_used and so should not be called separately

            if not any("re." in line for line in self.baseball_file_contents):
                self.feedback += "<li>re module is not used in file.</li>"
                self.points_deducted += 8

        def check_if_string_methods_are_used(self):
            split_used = False
            if any(".split" in line for line in self.baseball_file_contents):
                split_used = True

            uses_regex = self.check_if_re_is_used()
            if split_used and uses_regex:
                self.feedback += "<li>You used regex, but you also used str.split(). You should only use regex.</li>"
                self.points_deducted += 4

        def grade(self):
            self.check_if_string_methods_are_used()

    class UsageMessageGrader(BaseGrader):
        def __init__(self, input_file_path):
            super().__init__(input_file_path)
            self.points_possible = 4
            self.result_of_file_execution = self.execute_file_no_args()

        def execute_file_no_args(self):
            response = subprocess.run(
                ["python", self.input_file_path], capture_output=True, text=True
            )
            return response.stdout + response.stderr

        def check_if_usage_message_is_correct(self):
            """
            Ask my custom Ollama model (based on qwen25:0.5b) to evaluate the usage message
            NOTE: You must first run the ./setup.sh script to set up the Ollama model used below
            """
            response: ChatResponse = chat(
                model="usage_message_eval",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
            filename: {self.input_file_path}
            positional args: cardinals_filepath
            usage message: {self.result_of_file_execution}
            """,
                    },
                ],
            )

            if "no" in response.message.content.lower():
                self.feedback += (
                    "<li>Usage message is either missing or insufficient</li>"
                )
                self.points_deducted += 4

        def grade(self):
            self.check_if_usage_message_is_correct()

    class BaseballOutputGrader(BaseGrader):
        def __init__(self, input_file_path):
            super().__init__(input_file_path)
            self.points_possible = 15
            self.expected_output_lines = []
            self.result_output_lines = []
            self.load_files()

        def load_files(self):
            with open(
                os.path.join(os.path.dirname(__file__), "expected_baseball_output.txt"),
                "r",
            ) as file:
                self.expected_output_lines = file.read().splitlines()

        def execute_file_and_save_output(self):
            result = subprocess.run(
                [
                    "python",
                    self.input_file_path,
                    os.path.join(os.path.dirname(__file__), "cardinals-1940.txt"),
                ],
                capture_output=True,
                text=True,
            ).stdout

            for line in result.splitlines():
                # this is necessary because sometimes students include titles for their output
                if re.match(r"^\w+\s+\w+\s*:\s*(?=\S*\d)\S+$", line):
                    self.result_output_lines.append(line)

        def clean_saved_output(self):
            self.result_output_lines = [
                line for line in self.result_output_lines if line
            ]

        def check_if_output_is_empty(self):
            invalid_output = ["", "\n", "\r\n", "\r"]
            if (
                self.result_output_lines in invalid_output
                or len(self.result_output_lines) == 0
            ):
                self.feedback += "<li>Program does not produce any output.</li>"
                self.points_deducted += 15

        def confirm_presence_of_delancy_and_mcgee(self):
            """
            Commonly left out of output
            """
            if not any(
                "DeLancey" in line for line in self.result_output_lines
            ) or not any("McGee" in line for line in self.result_output_lines):
                self.feedback += (
                    "<li>Delancy and/or McGee missing from the output.</li>"
                )
                self.points_deducted += 5

        def check_decimal_places(self):
            for i in range(len(self.result_output_lines)):
                pattern = r"\d+\.?\d{0,}"
                stat = re.search(pattern, self.result_output_lines[i])
                if not stat:
                    self.feedback += (
                        "<li>At least one of the computed values is missing</li>"
                    )
                    self.points_deducted += 3
                    return
                else:
                    stat = stat.group()
                if ("." in stat) and (len(stat.split(".")[1]) != 3):
                    self.feedback += "<li>Not all values have three decimal places</li>"
                    self.points_deducted += 3
                    return
                elif "." not in stat:
                    self.feedback += "<li>You are missing a decimal point in at least one of the computed values</li>"
                    self.points_deducted += 3
                    return

        def check_name_order(self):
            expected_order = [
                line.split(":")[0].strip() for line in self.expected_output_lines
            ]
            result_order = [
                line.split(":")[0].strip() for line in self.result_output_lines
            ]

            for i in range(len(expected_order)):
                if expected_order[i] != result_order[i]:
                    if (
                        result_order[i] == "Joe Medwick"
                        and expected_order[i] == "Terry Moore"
                    ) or (
                        result_order[i] == "Terry Moore"
                        and expected_order[i] == "Joe Medwick"
                    ):
                        continue  # these have the same stats, so order doesn't matter
                    else:

                        self.feedback += "<li>Output is ordered incorrectly</li>"
                        self.points_deducted += 5
                        break

        def confirm_calcuated_stats_are_correct(self):
            # for each line in the expected output, find the name
            for line in self.expected_output_lines:
                name = line.split(":")[0].strip()
                expected_stats = line.split(":")[1].strip()

                for result_line in self.result_output_lines:
                    if name in result_line:
                        actual_stat = re.search(r"\d+\.?\d{0,}", result_line)
                        if not actual_stat:
                            self.feedback += f"<li>Stats not calculated for {name}</li>"
                            self.points_deducted += 8
                            return
                        else:
                            actual_stat = actual_stat.group()
                        if float(expected_stats) != float(actual_stat):
                            self.feedback += f"<li>Stats calculated incorrectly. First noticed with {name} where {expected_stats} was expected.</li>"
                            self.points_deducted += 8
                            return

        def grade(self):
            self.execute_file_and_save_output()
            self.clean_saved_output()
            self.check_if_output_is_empty()
            self.confirm_presence_of_delancy_and_mcgee()
            self.check_decimal_places()
            self.check_name_order()
            self.confirm_calcuated_stats_are_correct()

    def grade(self):
        self.uses_regex_grader.grade()
        self.usage_message_grader.grade()
        self.baseball_output_grader.grade()

        self.points_deducted += (
            self.uses_regex_grader.points_deducted
            + self.usage_message_grader.points_deducted
            + self.baseball_output_grader.points_deducted
        )
