import re
from base_regex_grader import BaseRegexGrader


class Regex1Grader(BaseRegexGrader):
    def check_against_hello_world(self):
        good_sample = "hello world"
        if not re.match(self.regex, good_sample):
            self.feedback += "\nregex does not match 'hello world' when it should."

    def check_against_hello_frank(self):
        bad_sample = "hello frank"
        if re.match(self.regex, bad_sample):
            self.feedback += "\nregex matches 'hello frank' when it shouldn't."
            self.points_deducted += 5

    def grade(self):
        """
        Run all the tests and return the total points possible and points deducted.
        """
        self.check_against_hello_world()
        self.check_against_hello_frank()

        return self.points_possible, self.points_deducted
