import csv
from utilities import exit_with_error


# class to handle writing to the canvas csv file
# todo: add canvasapi support

class CanvasWriter:
    def __init__(self, args, grades_dict):
        self.args = args
        self.grades_dict = grades_dict

        self.input_file = open(args.canvas_template_file, "r")
        self.input_reader = csv.DictReader(self.input_file)

        self.outpath = args.canvas_template_file.split(".csv")[0] + "--OUTPUT.csv"
        self.output_file = open(self.outpath, "w")

        self.output_writer = csv.DictWriter(self.output_file, fieldnames=self.input_reader.fieldnames)

    def get_destination_column(self):
        # let the user choose which column to write the grades to

        print("Choose a column to write the grades to:")
        column_indexes = {}
        column_option_count = 0
        for i, column_name in enumerate(self.input_reader.fieldnames):
            # only allow columns that start with "Module"
            if column_name.startswith("Module"):
                column_option_count += 1

                column_indexes[column_option_count] = i
                print(f"{column_option_count}. {column_name}")

        while True:
            try:
                choice = int(input("Enter a number: "))
                if choice not in column_indexes.keys():
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        return column_indexes[choice]

    def write_grades(self, column_index):
        # first, write the header row
        self.input_file.seek(0)
        self.output_writer.writeheader()

        # write the grades to the chosen column

        for row_dict in self.input_reader:

            if row_dict["SIS User ID"] in self.grades_dict.keys() and row_dict["SIS User ID"] != "":
                if self.args.verbose:
                    print(f"SIS User ID: {row_dict['SIS User ID']}")
                    print(f"Grade: {self.grades_dict[row_dict['SIS User ID']]}")
                    print(f"Writing grade {self.grades_dict[row_dict['SIS User ID']]} to {row_dict['SIS User ID']}")
                row_dict[self.input_reader.fieldnames[column_index]] = self.grades_dict[row_dict["SIS User ID"]]

                self.output_writer.writerow(row_dict)

        self.input_file.close()
        self.output_file.close()
        if self.args.verbose:
            print(f"Grades written to {self.outpath}")

    def write(self):
        column_index = self.get_destination_column()
        self.write_grades(column_index)
