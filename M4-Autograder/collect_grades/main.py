import os

from github import Github
from Student import Student
import csv
import argparse

def connect_to_github():
    print("Connecting to Github...")
    # print the env variable
    print(os.environ.get("GH_TOKEN"))
    g = Github("zachicecreamcohn", os.environ.get("GH_TOKEN"))
    return g

def get_all_repos(g: Github):
    # confirm that we are logged in
    user = g.get_user()
    if user.login == "zachicecreamcohn":
        print("Logged in as zachicecreamcohn")

    # get all repos that start with module4-
    repos = g.get_organization("cse330-fall-2024").get_repos()

    M4_repos = []
    for repo in repos:
        if repo.name.startswith("module4-"):
            M4_repos.append(repo)

    # print the length of the list of repos
    print(f"M4 Repos Found: {len(M4_repos)}")

    return M4_repos


def record_individual_grade(student_id: str, grade: str, canvas_input: csv.DictReader, dict_writer: csv.DictWriter, error_file):
    # find the column with the header containing "Module 4"
    for i, column_name in enumerate(canvas_input.fieldnames):
        if "Module 4" in column_name:
            # loop through each row in the csv file. If the student ID matches, write the grade to the correct column
            for row_dict in canvas_input:
                # print(f"Comparing {row_dict['SIS User ID']} to {student_id}")
                # print(f"The value in the row has a length of {len(row_dict['SIS User ID'])} and the student ID has a "
                #       f"length of {len(student_id)}")
                row_value = row_dict["SIS User ID"]
                if row_value == student_id:
                    print(f"Writing grade {grade} to {student_id}")
                    row_dict[column_name] = grade
                    dict_writer.writerow(row_dict)
                    return
            # if it hasn't returned yet, it means the student ID wasn't found in the canvas csv file
            print(f"ERROR: {student_id} not found in canvas csv file")
            error_file.write(f"{student_id},,{grade}\n")
            return



def record_grades(repos: [Github], g: Github, canvas_template_path):
    if not os.path.exists(canvas_template_path):
        print("Error: canvas template file does not exist. Grades not recorded.")
        return

    with open(canvas_template_path, "r") as infile:
        canvas_csv_input = csv.DictReader(infile)
        dict_writer = csv.DictWriter(open("OUTPUT.csv", "w"), fieldnames=canvas_csv_input.fieldnames)
        dict_writer.writeheader()
        error_file = open("errors.csv", "w")

        # write header
        error_file.write("Student ID,Repo Name,Grade\n")

        repos_destination = os.path.join(os.getcwd(), "repos")
        for repo in repos:
            s = Student(g, repo, repos_destination)
            s.clone_repo()
            s.find_student_id()
            s.get_grade()


            # confirm that we have both the student ID and the grade
            if s.student_ID and s.grade:
                record_individual_grade(s.student_ID, s.grade, canvas_csv_input, dict_writer, error_file)

            else:
                error_file.write(f"{s.student_ID},{s.repo.name},{s.grade}\n")

            infile.seek(0)
            canvas_csv_input = csv.DictReader(infile)



    error_file.close()


def main(canvas_template_path):
    g = connect_to_github()
    repos = get_all_repos(g)
    record_grades(repos, g, canvas_template_path)


if __name__ == '__main__':
    # set up the argument parser
    # take in the canvas file path
    parser = argparse.ArgumentParser(description="Record grades from the M4 repos into the canvas csv file")

    # add the canvas file path argument
    parser.add_argument("canvas_template", help="The path to the canvas csv file")
    canvas_file = parser.parse_args().canvas_template
    main(canvas_file)
