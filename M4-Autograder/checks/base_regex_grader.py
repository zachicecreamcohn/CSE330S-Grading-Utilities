class BaseRegexGrader:
    def __init__(self, regex_file):
        self.points_possible = 5
        self.points_deducted = 0
        self.regex_file = regex_file
        self.feedback = ""
        self.regex = ""
        self.load_regex()


    def load_regex(self):
        """
        Load the regex from the file.
        """
        try:
            with open(self.regex_file, 'r') as file:
                self.regex = file.read().strip()
        except FileNotFoundError:
            self.feedback += "Regex file not found or incorrectly named.\n"
            self.points_deducted -= self.points_possible

    def compute_points(self):
        if self.points_deducted < 0:
            self.points_deducted = 0
        return self.points_possible - self.points_deducted
