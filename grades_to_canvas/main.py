# This is the main script to transfer grades from a csv file (google sheets form output) to canvas
#
# Note:
# this script requires a GRADE column to be present in the csv file. You should add this column using google sheets
# before exporting the csv file.

import argparse
from parse_csv import CSVParser
from canvas import CanvasWriter


# todo: use colorama for colored output
# todo: use canvasapi to interact with canvas
# todo: go through and add output if verbose is true to everything

def setup_argparse():
    parser = argparse.ArgumentParser(description="Transfer grades from google sheets csv to canvas")
    parser.add_argument("csv_file", help="csv file to read grades from")
    parser.add_argument("canvas_template_file", help="csv exported from canvas gradebook")

    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    return parser.parse_args()


def main():
    args = setup_argparse()

    csv_parser = CSVParser(args)
    grades_dict = csv_parser.parse()
    print(len(grades_dict.items()))
    canvas_writer = CanvasWriter(args, grades_dict)
    canvas_writer.write()

    pass

if __name__ == "__main__":
    main()
