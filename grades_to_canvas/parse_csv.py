# This is a class for handling the csv file.
import datetime
import os
import csv
from utilities import *
import re


class CSVParser:

    # constructor
    def __init__(self, args):

        # ensure all required arguments are present
        if args.csv_file is None or args.csv_file == "":
            exit_with_error("csv file not specified")

        # now, verify that the csv file exists and is a valid csv file
        if not args.csv_file.endswith(".csv") or not os.path.exists(args.csv_file):
            exit_with_error("Invalid csv file: " + args.csv_file)

        self.path = args.csv_file

        try:
            self.csv_file = open(self.path, "r+")
        except FileNotFoundError:
            exit_with_error("File not found: " + self.path)
        self.csv_reader = csv.DictReader(self.csv_file)

        self.problem_rows = []
        self.verbose = args.verbose
        self.student_grades = {}  # will be a dictionary of the form {student_id: grade}

    # check that the csv file has a GRADE column
    def verify_csv(self):
        # check that the csv file has a GRADE column
        if "GRADE" not in self.csv_reader.fieldnames:
            exit_with_error("csv file must have a GRADE column")

        # check that each row has a grade in the GRADE column (and that the grade is a number)
        for row_dict in self.csv_reader:

            if row_dict["GRADE"] == "" or row_dict["GRADE"] is None:
                self.problem_rows.append(row_dict)
                continue

            try:
                float(row_dict["GRADE"])
            except ValueError:
                self.problem_rows.append(row_dict)

        self.csv_file.seek(0)  # reset the csv file reader to the beginning of the file

    # get the student grades from the csv file
    def parse(self):
        # check that the csv file has a GRADE column
        self.verify_csv()

        for column_name in self.find_student_id_columns():
            for row_dict in self.csv_reader:

                if row_dict[column_name] == "" or row_dict in self.problem_rows or row_dict["GRADE"] == "GRADE":
                    continue

                student_id = row_dict[column_name]

                if student_id == "000000" or student_id == 000000:
                    self.problem_rows.append(row_dict)
                grade = row_dict["GRADE"]

                self.student_grades[student_id] = grade
            self.csv_file.seek(0)

        return self.student_grades

    def find_student_id_columns(self):
        found_columns = []

        for column_name in self.csv_reader.fieldnames:

            # check if the first non-header row in the column is a student id
            # if it is, add the column name to the list of student id columns
            for row_dict in self.csv_reader:
                if row_dict[column_name] == "":
                    continue

                if re.match(r"^\d{6}$", row_dict[column_name]):
                    found_columns.append(column_name)
                    break
            self.csv_file.seek(0)

        if len(found_columns) == 0:
            exit_with_error("No student id columns found")
        return found_columns

    def record_problem_rows(self):

        if len(self.problem_rows) == 0:
            return

        # create a new file to store the problem rows
        # it should be named "problem_rows_<MM-DD-YYYY_HH-MM-SS>.csv"

        # get the current date and time
        now = datetime.datetime.now()
        formatted_now = now.strftime("%m-%d-%Y_%H-%M-%S")
        problem_rows_file_name = "problem_rows_" + formatted_now + ".csv"

        # if a directory called "Skipped Rows" doesn't exist, create it
        if not os.path.exists("Skipped Rows"):
            os.mkdir("Skipped Rows")

        problem_rows_file = open("Skipped Rows/" + problem_rows_file_name, "w", newline='')
        csv_writer = csv.DictWriter(problem_rows_file, fieldnames=self.csv_reader.fieldnames)

        csv_writer.writeheader()  # write the header row

        for row_dict in self.problem_rows:
            csv_writer.writerow(row_dict)

        problem_rows_file.close()

    def __del__(self):
        try:
            self.record_problem_rows()
        except AttributeError:
            pass
        try:
            self.csv_file.close()
        except AttributeError:
            pass
