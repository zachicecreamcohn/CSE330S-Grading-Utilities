from graders.base_grader import BaseGrader


class BaseRegexGrader(BaseGrader):
    def __init__(self, input_file_path):
        super().__init__(input_file_path)
        self.points_possible = 5
        self.regex = ""
        self.load_regex()

    def load_regex(self):
        """
        Load the regex from the file.
        """
        try:
            with open(self.input_file_path, "r") as file:
                self.regex = file.read().strip()
        except FileNotFoundError:
            self.feedback += "Regex file not found or incorrectly named.\n"
            self.points_deducted -= self.points_possible
