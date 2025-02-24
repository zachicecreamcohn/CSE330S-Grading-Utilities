import re
from graders.base_regex_grader import BaseRegexGrader


class Regex3Grader(BaseRegexGrader):

    def check_four_number_AA_sample(self):
        good_sample = "AA1234"
        if not re.match(self.regex, good_sample):
            self.feedback += "<li>regex does not match 'AA1234' when it should.</li>"
            self.points_deducted += 5

    def check_three_number_AA_sample(self):
        good_sample = "AA123"
        if not re.match(self.regex, good_sample):
            self.feedback += "<li>regex does not match 'AA123' when it should.</li>"
            self.points_deducted += 5

    def confirm_non_AA_four_number_sample(self):
        good_sample = "BZ1234"
        if not re.match(self.regex, good_sample):
            self.feedback += "<li>regex does not match 'BZ1234' when it should.</li>"
            self.points_deducted += 5

    def confirm_non_AA_three_number_sample(self):
        good_sample = "BZ123"
        if not re.match(self.regex, good_sample):
            self.feedback += "<li>regex does not match 'BZ123' when it should.</li>"
            self.points_deducted += 5

    def check_if_matches_5_digit_sample(self):
        bad_sample = "AA12345"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches 'AA12345' when it shouldn't. Flight code must have 3 or 4 numbers.</li>"
            self.points_deducted += 5

    def check_if_matches_2_digit_sample(self):
        bad_sample = "AA12"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches 'AA12' when it shouldn't. Flight code must have 3 or 4 numbers.</li>"
            self.points_deducted += 5

    def check_if_matches_sample_ending_in_letter(self):
        bad_sample = "AA123A"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches 'AA123A' when it shouldn't. Flight code must end with a number.</li>"
            self.points_deducted += 5

    def confirm_only_matches_when_first_two_are_letters(self):
        bad_sample = "11234"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches '11234' when it shouldn't. Flight code must start with two letters.</li>"
            self.points_deducted += 5

    def confirm_only_matches_capital_starting_letters(self):
        bad_sample = "aa1234"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches 'aa1234' when it shouldn't. Flight code must start with two capital letters.</li>"
            self.points_deducted += 5

    def confirm_only_matches_one_flight_code(self):
        bad_sample = "AA1234 AA123"
        if re.match(self.regex, bad_sample):
            self.feedback += "<li>regex matches 'AA1234 AA123' when it shouldn't. Should only match if the input is a single flight code.</li>"
            self.points_deducted += 2

    def grade(self):
        """
        Run all the tests and return the total points possible and points deducted.
        """
        self.check_four_number_AA_sample()
        self.check_three_number_AA_sample()
        self.confirm_non_AA_four_number_sample()
        self.confirm_non_AA_three_number_sample()
        self.check_if_matches_5_digit_sample()
        self.check_if_matches_2_digit_sample()
        self.check_if_matches_sample_ending_in_letter()
        self.confirm_only_matches_when_first_two_are_letters()
        self.confirm_only_matches_capital_starting_letters()
        self.confirm_only_matches_one_flight_code()
