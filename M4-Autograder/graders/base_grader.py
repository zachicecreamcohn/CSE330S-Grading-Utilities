from abc import abstractmethod


class BaseGrader:
    def __init__(self, input_file_path=""):
        self.points_possible = 0  # should be redefined in the child class
        self.points_deducted = 0
        self.input_file_path = input_file_path
        self.feedback = ""

    @abstractmethod
    def grade(self):
        pass

    def compute_points(self):
        if self.points_deducted < 0:
            self.points_deducted = 0
        return self.points_possible - self.points_deducted

    def get_points_deducted(self):
        return self.points_deducted

    def get_feedback(self):
        return self.feedback
