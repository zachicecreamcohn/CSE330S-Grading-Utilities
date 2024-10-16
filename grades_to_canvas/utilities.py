import sys


def exit_with_error(message):
    # todo: add colorama support so that the error message is red
    print(f"Error: {message}\n")
    sys.exit(1)
