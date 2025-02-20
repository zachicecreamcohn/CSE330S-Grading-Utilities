import re
from base_regex_grader import BaseRegexGrader


class Regex2Grader(BaseRegexGrader):
    def check_sample_with_no_matches(self):
        bad_sample = "The quick brown fox jumps over the lazy dog"
        if re.search(self.regex, bad_sample):
            self.feedback += "\nregex matches 'The quick brown fox jumps over the lazy dog' when it shouldn't."
            self.points_deducted += 5

    def check_sample_with_two_matches(self):
        good_sample = "The gooey peanut butter and jelly sandwich was beautiful"
        if not re.search(self.regex, good_sample):
            self.feedback += "\nregex does not match 'The gooey peanut butter and jelly sandwich was beautiful' when it should match 'gooey' and 'beautiful'."
            self.points_deducted += 5

    def check_for_mixed_case(self):
        good_mixed_case_sample = "the GoOeY bEaUtY"
        good_lowercase_sample = "the gooey beauty"
        if not re.search(self.regex, good_mixed_case_sample) and re.search(
            self.regex, good_lowercase_sample
        ):
            self.feedback += "\nregex does not account for mixed case when it should."
            self.points_deducted += 2

    def check_that_it_matches_multiple_words(self):
        good_sample = "The gooey peanut butter and jelly sandwich was beautiful"
        if len(re.findall(self.regex, good_sample)) < 2:
            self.feedback += "\nregex does not match multiple words containg at least three consecutive vowels when it should."
            self.points_deducted += 3

    def check_that_it_matches_entire_word(self):
        good_sample = "gooey"
        # check if it only matches the consecutive vowel substring and not the entire words
        regex_result = re.search(self.regex, good_sample)
        if regex_result and (
            regex_result.group() == "ooe"
            or regex_result.group() == "ooey"
            or regex_result.group() == "eey"
        ):
            self.feedback += "\nregex matches the consecutive vowel substring of the word when it should match the entire word."
            self.points_deducted += 3

    def grade(self):
        """
        Run all the tests and return the total points possible and points deducted.
        """
        self.check_sample_with_no_matches()
        self.check_sample_with_two_matches()
        self.check_for_mixed_case()
        self.check_that_it_matches_multiple_words()
        self.check_that_it_matches_entire_word()

        return self.points_possible, self.points_deducted
