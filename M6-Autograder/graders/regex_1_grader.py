import re
from graders.base_regex_grader import BaseRegexGrader


class Regex1Grader(BaseRegexGrader):
    def check_against_hello_world(self):
        good_sample = "hello world"
        if not re.match(self.regex, good_sample):
            self.feedback += (
                "<li>regex does not match 'hello world' when it should.</li>"
            )

    def check_against_hello_frank(self):
        bad_sample = "hello frank"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches 'hello frank' when it shouldn't.</li>"
            self.points_deducted += 5

    def grade(self):
        """
        Run all the tests and return the total points possible and points deducted.
        """
        self.check_against_hello_world()
        self.check_against_hello_frank()
