import os
import shutil
import subprocess
# allow for regex
import re
import time
# first, get all repos for the module
# all repos are named module4-<github username>
# they are all in the same github organization

# then, for each repo, clone it

from github import Github


def connect_to_github():
    # get key from env
    g = Github("zachicecreamcohn", os.getenv.get("GH_TOKEN"))
    return g


def get_all_repos():
    # check if the temp directory exists
    if not os.path.exists("M4_grading_temp"):
        os.mkdir("M4_grading_temp")

    g = connect_to_github()

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

    # return an array of the urls of the repos
    return (M4_repos, g)

    # # clone each repo into the new directory
    cloned_count = 0
    for repo in M4_repos:
        # check if the repo has already been cloned
        if not os.path.exists(f"module4_repos/{repo.name}"):
            # clone the repo using the github api
            # g.get_repo(f"cse330-spring-2023/{repo.name}").clone_url
            # the same as above, but using the command line
            os.system(f"git clone {repo.clone_url} module4_repos/{repo.name}")
            cloned_count += 1

        if repo == M4_repos[-1]:
            if cloned_count == 0:
                print("All repos already cloned!")
            else:
                print(
                    f"All repos cloned! and saved in {os.path.abspath('module4_repos')}")
                print(f"Cloned {cloned_count} repos")

            # print how many repos are in the directory
            print(
                f"Number of repos in directory: {len(os.listdir('module4_repos'))}")


# a class for each student
# will hold their work and contains methods for grading
class Student:
    def __init__(self, name, repo, g=None):
        self.g = g
        self.name = name
        self.repo = repo  # the repo object (from github api )

        # define variables for the student's work
        # first, regex
        self.regex = {
            "1": r"",
            "2": r"",
            "3": r"",
        }

        self.grades = {
            "regex": {
                "1": {
                    "possible": 5,
                    "earned": 0,
                    "comment": ""
                },
                "2": {
                    "possible": 5,
                    "earned": 0,
                    "comment": ""
                },
                "3": {
                    "possible": 5,
                    "earned": 0,
                    "comment": ""
                },
            },
            "baseball": {
                "free points": {
                    "possible": 8,
                    "earned": 8,
                    "comment": ""
                },
                "uses regex": {
                    "possible": 8,
                    "earned": 0,
                    "comment": ""
                },
                "usage message": {
                    "possible": 4,
                    "earned": 0,
                    "comment": ""
                },
                "correct output": {
                    "possible": 15,
                    "earned": 0,
                    "comment": ""
                },
            },

        }

        # define a variable for the student's total grade
        self.total_grade = 0

    # a method to clone the student's repo
    def clone_repo(self, clone):

        if not clone:
            print(f"Skipping cloning {self.repo.name}")
            return


        # check if a directory for the student's repo exists already
        if os.path.exists(f"M4_grading_temp/{self.repo.name}"):
            print(f"{self.repo.name} already cloned. Skipping")
            return
        #
        # first, connect to github
        g = self.g

        # confirm that we are logged in
        user = g.get_user()
        if (user.login == "zachicecreamcohn"):
            # now, if it doesn't already exist, make a directory called "M4_grading_temp"
            if not os.path.exists("M4_grading_temp"):
                os.mkdir("M4_grading_temp")

            # check if the repo has already been cloned
            if not os.path.exists(f"M4_grading_temp/{self.repo.name}"):
                os.system(f"git clone {self.repo.clone_url} M4_grading_temp/{self.repo.name}")

            if "grading" not in [branch.name for branch in self.repo.get_branches()]:
                os.system(f"cd M4_grading_temp/{self.repo.name} && git checkout -b grading")

            # clone the repo into the temp directory
            # create new branch for grading
            # repos will be moved into a graded directory after grading is complete

    # a method to grade the student's regex
    def grade_all_regex(self):
        filenames = ["regex1.txt", "regex2.txt", "regex3.txt"]
        for filename in filenames:
            path = locate_file(filename, f"M4_grading_temp/{self.repo.name}")
            if path == None:
                print(f"{filename} not found in {self.repo.name}")
                continue
            else:

                # now, parse and grade the regex
                regex_num = int(filename[5])
                self.grade_regex(path, regex_num)

    def parse_regex_file(self, path, regex_num):
        with open(path, "r") as f:
            regex = f.read().replace('\r\n', '\n').replace('\r', '\n')  # Normalize line endings
        lines = [line.strip() for line in regex.split('\n') if
                 line.strip() and not line.startswith('#') and not line.startswith('//') and not line.startswith('/*')]
        regex = ''.join(lines)

        # now, check if a student has forgotten to exclude the quotes or raw string '/' characters
        if regex.startswith('"') or regex.startswith("'"):
            regex = regex[1:]
        if regex.endswith('"') or regex.endswith("'"):
            regex = regex[:-1]

        if regex.startswith("r'") or regex.startswith('r"'):
            regex = regex[2:]
        if regex.endswith("r'") or regex.endswith('r"'):
            regex = regex[:-2]

        if regex.startswith("/"):
            regex = regex[1:]
        if regex.endswith("/"):
            regex = regex[:-1]

        if regex.endswith("/g"):
            regex = regex[:-2]

        if (regex != ""):
            # save regex to self.regex
            self.regex[regex_num] = regex
            return regex
        else:
            print(f"Regex {regex_num} in {self.repo.name} is empty")
            return None

    # a method to grade regex
    def grade_regex(self, path_to_regex, regex_num):
        print(f"{self.repo.name} regex {regex_num} path: {path_to_regex}")
        # get the regex from the student's file

        regex = self.parse_regex_file(path_to_regex, regex_num)

        if regex == None:
            print(f"Regex {regex_num} not found in {self.repo.name}")
            return

        if (regex_num == 1):
            print(regex)

            print(f"Grading regex {regex_num} in {self.repo.name}")
            # check if regex correctly matches "hello world"
            bad_sample = "hello frank"
            good_sample = "hello world"
            if re.search(regex, bad_sample) != None:
                self.grades["regex"]["1"]["comment"] += f"Regex {regex_num} matches '{bad_sample}' when it should not."
            if re.search(regex, good_sample) == None:
                self.grades["regex"]["1"][
                    "comment"] += f"Regex {regex_num} does not match '{good_sample}' when it should."
            if self.grades["regex"]["1"]["comment"] == "":
                self.grades["regex"]["1"]["earned"] = 5
                self.grades["regex"]["1"]["comment"] = ""
            else:
                self.grades["regex"]["1"]["earned"] = 0

            return  # don't need to check the other regexes
        elif (regex_num == 2):
            print(f"Grading regex {regex_num} in {self.repo.name}")
            # check that regex matches all words in an input string that contain three consecutive vowels, regardless of case.
            sample_1 = "The quick brown fox jumped over the lazy dog"
            # should match no words because there are no words with three consecutive vowels
            sample_2 = "The gooey peanut butter and jelly sandwich was a beauty."
            # should match gooey and beauty because they contain three consecutive vowels
            case_testing = "the GoOeY bEaUtY"
            # should match GoOeY and bEaUtY because they contain three consecutive vowels
            if re.search(regex, sample_1) != None:
                self.grades["regex"]["2"]["comment"] += f"Regex {regex_num} matches '{sample_1}' when it should not. "
                # give a 0
                self.grades["regex"]["2"]["earned"] = 0
                return  # don't need to check the other regexes

            points_earned = 5  # start with 5 points and deduct points for each error

            # check that both "gooey" and "beauty" are matched
            if re.search(regex, sample_2) == None:
                self.grades["regex"]["2"]["comment"] += f"Regex {regex_num} does not match '{sample_2}' when it should."
                points_earned -= 5
                self.grades["regex"]["2"]["earned"] = points_earned
                return
            else:
                # get an array of all matches
                matches = re.findall(regex, sample_2)

                # check that both "gooey" and "beauty" are matched
                if "gooey" in matches and "beauty" in matches:
                    # both are matched
                    pass
                elif "gooey" in matches or "beauty" in matches:
                    # only one is matched
                    self.grades["regex"]["2"][
                        "comment"] += f"Regex {regex_num} only matches one of the words in '{sample_2}' when it should match both. "
                    points_earned -= 2
                else:

                    # check if the matches are inside of "gooey" and "beauty"
                    for match in matches:
                        if match in "gooey" or match in "beauty" and match != "gooey" and match != "beauty":
                            # the match is inside of "gooey" or "beauty"
                            self.grades["regex"]["2"][
                                "comment"] += f"Regex {regex_num} matches a substring of a word in '{sample_2}' when it should match the entire word."
                            points_earned -= 2
                            self.grades["regex"]["2"]["earned"] = points_earned
                            return

                    # neither is matched
                    self.grades["regex"]["2"][
                        "comment"] += f"Regex {regex_num} does not match either of the words in '{sample_2}' when it should match both."
                    points_earned -= 5
                    self.grades["regex"]["2"]["earned"] = points_earned
                    return

                # check that the regex is case insensitive
                if re.search(regex, case_testing) == None:
                    self.grades["regex"]["2"][
                        "comment"] += f"Regex {regex_num} does not match '{case_testing}' when it should."
                    points_earned -= 2
                else:
                    # assume that the regex is case insensitive
                    pass

                # check how many points were earned
                if points_earned == 5:
                    self.grades["regex"]["2"]["earned"] = 5
                    self.grades["regex"]["2"]["comment"] = ""
                else:
                    # if points earned is 1 (meaning 2 was deducted twice), then set it to 0
                    if points_earned == 1:
                        points_earned = 0
                    self.grades["regex"]["2"]["earned"] = points_earned

            return  # don't need to check the other regexes
        elif (regex_num == 3):
            print(f"Grading regex {regex_num} in {self.repo.name}")

            points_earned = 5  # start with 5 points and deduct points for each error
            good_sample_1 = "AA1234"
            good_sample_2 = "AA123"
            good_sample_3 = "BZ1234"
            good_sample_4 = "BZ123"
            newline_sample = "AA123\n"

            bad_sample_1 = "AA12345"
            bad_sample_2 = "AA123A"
            bad_sample_3 = "aa1234"

            bad_sample_4 = "AA123 AB1234"

            # first, check that all good samples are matched
            if re.search(regex, good_sample_1) == None or re.search(regex, good_sample_2) == None or re.search(regex,
                                                                                                               good_sample_3) == None or re.search(
                regex, good_sample_4) == None:

                # check if newline_sample is matched
                if re.search(regex, newline_sample) != None:
                    self.grades["regex"]["3"][
                        "comment"] += f"Regex {regex_num} matches sample with a newline on the end when it should not."
                    points_earned -= 2
                    return

                self.grades["regex"]["3"][
                    "comment"] += (f"Regex {regex_num} does not match all of the good samples when it should. "
                                   f"Specifically,")

                if re.search(regex, good_sample_1) is None:
                    self.grades["regex"]["3"]["comment"] += f"'{good_sample_1}', "
                if re.search(regex, good_sample_2) is None:
                    self.grades["regex"]["3"]["comment"] += f"'{good_sample_2}', "
                if re.search(regex, good_sample_3) is None:
                    self.grades["regex"]["3"]["comment"] += f"'{good_sample_3}', "
                if re.search(regex, good_sample_4) is None:
                    self.grades["regex"]["3"]["comment"] += f"'{good_sample_4}', "

                points_earned -= 5
                self.grades["regex"]["3"]["earned"] = points_earned
                return

            else:
                # ensure that none of the bad samples (1-3) are matched
                bad_sample_matched = False
                if re.search(regex, bad_sample_1):
                    bad_sample_matched = bad_sample_1
                    self.grades["regex"]["3"][
                        "comment"] += f"Regex {regex_num} matches bad sample '{bad_sample_matched}' when it should not. Flight code must have between 3 and four digits."
                elif re.search(regex, bad_sample_2):
                    bad_sample_matched = bad_sample_2
                    self.grades["regex"]["3"][
                        "comment"] += f"Regex {regex_num} matches bad sample '{bad_sample_matched}' when it should not. Flight Code must be two uppercase letters followed by 3-4 digits. Can't end in a number."

                elif re.search(regex, bad_sample_3):
                    bad_sample_matched = bad_sample_3
                    self.grades["regex"]["3"][
                        "comment"] += f"Regex {regex_num} matches bad sample '{bad_sample_matched}' when it should not. Flight Code must be two uppercase letters followed by 3-4 digits. Can't start with a lowercase letter."
                elif re.search(regex, bad_sample_4):
                    bad_sample_matched = bad_sample_4
                    self.grades["regex"]["3"][
                        "comment"] += f"Regex {regex_num} matches bad sample '{bad_sample_matched}' when it should not. Regex should only match a line with only ONE flight code in it."

                if bad_sample_matched:
                    points_earned -= 5
                    self.grades["regex"]["3"]["earned"] = points_earned
                    return
                else:
                    # check if it matches multiple flight codes in one string (bad_sample_4). It should not. If it does, deduct 2 points

                    # get an array of all matches
                    matches = re.findall(regex, bad_sample_4)
                    if len(matches) > 1:
                        self.grades["regex"]["3"][
                            "comment"] += f"Regex {regex_num} matches multiple flight codes in '{bad_sample_4}' when it should not."
                        points_earned -= 2
                    else:
                        # check if it matches the first flight code ("AA123")
                        if "AA123" in matches:
                            self.grades["regex"]["3"][
                                "comment"] += f"Regex {regex_num} matches the first flight code in '{bad_sample_4}' when it should not. The expectation is that you match a flightcode only when it is the only thing in the sample "
                            points_earned -= 2

            # check how many points were earned
            if points_earned == 5:
                self.grades["regex"]["3"]["earned"] = 5
                self.grades["regex"]["3"]["comment"] = ""
            else:
                # if points earned is 1 (meaning 2 was deducted twice), then set it to 0
                if points_earned == 1:
                    points_earned = 0
                self.grades["regex"]["3"]["earned"] = points_earned

            return  # don't need to check the other regexes

    def grade_all_baseball(self):
        path_to_baseball = locate_file("baseball.py", f"M4_grading_temp/{self.repo.name}")
        self.check_if_uses_regex(path_to_baseball)
        self.confirm_that_program_prints_usage_message(path_to_baseball)
        self.check_baseball_output(path_to_baseball)

        return

    def check_if_uses_regex(self, path_to_baseball):
        points_earned = 8
        # first, check if str.split() is used anywhere in the file
        # "str" in str.split() could be any string variable

        with open(path_to_baseball, "r") as f:
            for line in f:
                if ".split(" in line:
                    # check that it's not re.split()
                    if "re.split(" in line:
                        # skip this line
                        pass
                    points_earned -= 4  # deduct 4 points. If they don't use any regex, they will get 0 points
                    break

        # now, verify that regex is used.
        # to determine this, we will check if re is imported and if re.* is used anywhere in the file
        re_imported = False
        re_used = False
        with open(path_to_baseball, "r") as f:
            for line in f:
                if "import re" in line or "re" in line:
                    # re is imported
                    re_imported = True
                if "re." in line:
                    # re is used
                    re_used = True

        if re_imported == False:
            self.grades["baseball"]["uses regex"]["comment"] += "You did not import re. No regex was used."
            points_earned = 0
        elif re_used == False:
            self.grades["baseball"]["uses regex"]["comment"] += "You did not use any regex. "
            points_earned = 0
        else:
            # regex is used.
            if (points_earned == 4):
                self.grades["baseball"]["uses regex"][
                    "comment"] += "You used regex, but you used str.split() as well. You should only use regex. "
            else:
                self.grades["baseball"]["uses regex"]["comment"] = ""

        self.grades["baseball"]["uses regex"]["earned"] = points_earned

    def confirm_that_program_prints_usage_message(self, path_to_baseball):
        # execute the python file located at path_to_baseball and check if it prints the usage message

        # first, check if the file exists
        if os.path.exists(path_to_baseball) == False:
            self.grades["baseball"]["usage message"]["comment"] += "The file baseball.py does not exist. "
            self.grades["baseball"]["usage message"]["earned"] = 0
            return

        # now, execute the file from the command line. Don't pass any arguments
        file_output = subprocess.run(["python3", path_to_baseball], capture_output=True, text=True)

        # check if the usage message is printed
        # if the output is empty, then the program did not print anything
        if "usage" in file_output.stderr.lower() or "usage" in file_output.stdout.lower():
            self.grades["baseball"]["usage message"]["comment"] = ""
            self.grades["baseball"]["usage message"]["earned"] = 4
        else:
            self.grades["baseball"]["usage message"]["comment"] += "The program does not print a usage message. "
            self.grades["baseball"]["usage message"]["earned"] = 0

        return

    def check_baseball_output(self, path_to_baseball):
        # execute the python file located at path_to_baseball and store the output

        # pass in the path to cardinals-1940.txt as an argument
        sample_file = "/Users/zacharycohn/Documents/WashU/330TA/Utilities/M4-Autograder/cardinals-1940.txt"

        baseball_exec = subprocess.run(["python3", path_to_baseball, sample_file], capture_output=True, text=True)
        self.baseball_output = baseball_exec.stdout

        # now, split the output into an array of lines
        output_lines = self.baseball_output.splitlines()

        # do the same for the expected output
        expected_output_file = "/Users/zacharycohn/Documents/WashU/330TA//Utilities/M4-Autograder/1940-correct-output.txt"
        with open(expected_output_file, "r") as f:

            expected_output = f.read()
        expected_output_lines = expected_output.splitlines()

        # loop through the lines and remove any empty lines or lines that only contain whitespace/newlines
        output_lines = [line for line in output_lines if line.strip() != ""]

        # loop through the lines and check if they match
        points_earned = 15

        no_output = False  # award 0 points
        values_miscalculated = False  # -8 points
        DeLancy_or_McGee_missing = False  # -5 points
        not_three_decimal_places = False  # -3 points
        not_sorted = False  # -5 points
        problem_lines = []

        # check if the output is empty
        if len(output_lines) == 0:
            self.grades["baseball"]["correct output"]["comment"] += "The program does not print any output. "
            self.grades["baseball"]["correct output"]["earned"] = 0
            return

        found_deLancy = False
        found_mcGee = False
        # check if McGee or DeLancy are missing
        for line in output_lines:
            if "DeLancey" in line:
                found_deLancy = True
            if "McGee" in line:
                found_mcGee = True

        if not found_deLancy or not found_mcGee:
            DeLancy_or_McGee_missing = True

        expected_names_in_order = ["Pepper Martin", "Walker Cooper", "Johnny Mize", "Ernie Koy", "Enos Slaughter",
                                   "Joe Medwick", "Terry Moore", "Joe Orengo", "Jimmy Brown", "Marty Marion",
                                   "Don Gutteridge", "Johnny Hopp", "Creepy Crespi", "Mickey Owen", "Bill DeLancey",
                                   "Don Padgett", "Stu Martin", "Eddie Lake", "Hal Epps", "Lon Warneke", "Harry Walker",
                                   "Max Lanier", "Bill McGee", "Carl Doyle", "Mort Cooper", "Clyde Shoun",
                                   "Carden Gillenwater", "Bob Bowman"]

        # check if the order of the output is correct
        for i in range(len(output_lines)):

            name = output_lines[i].split(":")[0].strip()

            if name != expected_names_in_order[i]:
                # check if it's an issue with Terry Moore and Joe Medwick. They have the same batting average
                if name == "Joe Medwick" and expected_names_in_order[i] == "Terry Moore" or name == "Terry Moore" and \
                        expected_names_in_order[i] == "Joe Medwick":
                    continue
                elif name == "Walker Cooper" and expected_names_in_order[
                    i] == "Pepper Martin" or name == "Pepper Martin" and expected_names_in_order[i] == "Walker Cooper":
                    continue
                elif expected_names_in_order[i] == "Bill DeLancey" and name in "Bill DeLancey" or \
                        expected_names_in_order[i] == "Bill McGee" and name in "Bill McGee":
                    self.grades["baseball"]["correct output"][
                        "comment"] += f"{name} should be spelled correctly, as {expected_names_in_order[i]} "
                    # DeLancy_or_McGee_missing = True
                    continue

                    self.grades["baseball"]["correct output"][
                        "comment"] += f"{name} is in the wrong place. Should be {expected_names_in_order[i]}. "
                    # the order is incorrect
                    not_sorted = True
                    break

        if not_sorted:
            new_output_lines = []
            # sort the output so it matches the expected output
            for name in expected_names_in_order:
                for line in output_lines:
                    # skip the line if it's empty or a newline
                    if line == "" or line == "\n":
                        continue
                    else:

                        if name in line:
                            new_output_lines.append(line)
                            break
            output_lines = new_output_lines
            # now, loop through the lines and remove any blank lines
            new_output_lines = []
            for line in output_lines:
                if line == "" or line == "\n":
                    continue
                else:
                    new_output_lines.append(line)
            output_lines = new_output_lines

        for i in range(len(output_lines)):

            name = output_lines[i].split(":")[0].strip()
            stat = output_lines[i].split(":")[1].strip()

            # do the same thing for the expected output
            expected_name = expected_output_lines[i].split(":")[0].strip()
            expected_stat = expected_output_lines[i].split(":")[1].strip()

            # check if the names match
            if name != expected_name:
                # check first if the name is "Joe Medwick" and expected name is "Terry Moore" or vice versa
                if (name == "Joe Medwick" and expected_name == "Terry Moore") or (
                        name == "Terry Moore" and expected_name == "Joe Medwick"):
                    # this is a special case. The names have the same stats
                    pass
                else:
                    print(f"Name on line {i} does not match")
                    print(f"Expected: {expected_name}")
                    print(f"Actual: {name}")
                    print("\n")

                    # append a tuple containing the problem line and the line
                    problem_lines.append((output_lines[i], expected_output_lines[i]))
            else:
                # the names match. Check if the stats match
                if stat != expected_stat:

                    stat = float(stat)
                    expected_stat = float(expected_stat)
                    # check if the output stat is just a different number of decimal places than the expected stat
                    if stat == expected_stat:
                        # the stats are the same, but the output is not formatted correctly
                        if ("Different number of decimal places" not in self.grades["baseball"]["correct output"][
                            "comment"]):
                            self.grades["baseball"]["correct output"][
                                "comment"] += f"Different number of decimal places."
                        not_three_decimal_places = True

                    else:
                        values_miscalculated = True

                    print(f"Stats on line {i} do not match")
                    print(f"Expected: {expected_stat}")
                    print(f"Actual: {stat}")
                    print("\n")
                    problem_lines.append((output_lines[i], expected_output_lines[i]))

        if (values_miscalculated):
            self.grades["baseball"]["correct output"]["comment"] += "The output is incorrect."
            points_earned -= 8
        if (DeLancy_or_McGee_missing):
            if (found_deLancy and not found_mcGee):
                self.grades["baseball"]["correct output"]["comment"] += "McGee is missing."
            elif (found_mcGee and not found_deLancy):
                self.grades["baseball"]["correct output"]["comment"] += "DeLancy is missing."
            else:
                self.grades["baseball"]["correct output"]["comment"] += "DeLancy and McGee are missing."
            points_earned -= 5
        if (not_three_decimal_places):
            self.grades["baseball"]["correct output"]["comment"] += "The output is not formatted correctly."
            points_earned -= 3

        if (not_sorted):
            self.grades["baseball"]["correct output"]["comment"] += "The output is not sorted correctly."
            points_earned -= 5

        if (no_output):
            self.grades["baseball"]["correct output"]["comment"] += "The program does not print any output."
            points_earned = 0

        if points_earned < 0:
            points_earned = 0

        self.grades["baseball"]["correct output"]["earned"] = points_earned

        print(f"Points earned: {points_earned}")
        if (points_earned < 15):
            print(f"Feedback: {self.grades['baseball']['correct output']['comment']}")
        return

    def tally_grades(self):
        # tally the grades
        total_points = 0
        possible_points = 0
        for section in self.grades.keys():
            for title in self.grades[section].keys():
                total_points += self.grades[section][title]["earned"]
                possible_points += self.grades[section][title]["possible"]

        grades_explanation = f"""

## Regex

| Title | Possible Points | Points Earned | Explanation |
| --- | --- | --- | --- |
| Regex1 | {self.grades['regex']['1']['possible']} | {self.grades['regex']['1']['earned']} | {self.grades['regex']['1']['comment'].strip()} |
| Regex2 | {self.grades['regex']['2']['possible']} | {self.grades['regex']['2']['earned']} | {self.grades['regex']['2']['comment'].strip()} |
| Regex3 | {self.grades['regex']['3']['possible']} | {self.grades['regex']['3']['earned']} | {self.grades['regex']['3']['comment'].strip()} |

## Baseball

| Title | Possible Points | Points Earned | Explanation |
| --- | --- | --- | --- |
| File called baseball.py | {self.grades['baseball']['free points']['possible']} | {self.grades['baseball']['free points']['earned']} | {self.grades['baseball']['free points']['comment']} |
| Uses Regex to parse input | {self.grades['baseball']['uses regex']['possible']} | {self.grades['baseball']['uses regex']['earned']} | {self.grades['baseball']['uses regex']['comment']} |
| Usage Message | {self.grades['baseball']['usage message']['possible']} | {self.grades['baseball']['usage message']['earned']} | {self.grades['baseball']['usage message']['comment']} |
| Correct Output | {self.grades['baseball']['correct output']['possible']} | {self.grades['baseball']['correct output']['earned']} | {self.grades['baseball']['correct output']['comment']}


# Total Points
{total_points} / {possible_points}

"""

        return grades_explanation

    def edit_readme(self, grades_explanation):

        # Create new branch called "grading"
        # use self.g to create a new branch

        # get the readme file
        readme = locate_file("README.md", f"M4_grading_temp/{self.repo.name}")
        # open the readme file
        with open(readme, "r+") as f:
            # read the contents of the file
            contents = f.read()

            # write to end of file
            f.write(grades_explanation)

        self.add_commit_push()

        return

    def add_commit_push(self):

        if not args.individual:
            initial_dir = os.getcwd()
            # add, commit, and push the changes

            # use command line commands to add, commit, and push the changes

            # add the changes
            os.system(f"cd M4_grading_temp/{self.repo.name} && git add .")

            # commit the changes
            os.system(f"cd M4_grading_temp/{self.repo.name} && git commit -m 'grading'")

            # push the changes

            os.system(f"cd M4_grading_temp/{self.repo.name} && git push --set-upstream origin grading")

            # cd back to the main directory
            os.system(f"cd {initial_dir}")

        return


def locate_file(file_name, path):
    for root, dirs, files in os.walk(path):
        if file_name in files:
            return os.path.join(root, file_name)


import time


# a method to test the autograder
def run_autograder(clone, test):
    print("Running autograder")
    get_all_repos_response = get_all_repos()
    g = get_all_repos_response[1]
    repos = get_all_repos_response[0]
    repo_count = len(repos)
    # if test:
    # repo_to_check = input("Enter the repo name to test: ")
    for repo in repos:
        print(f"Repo #{repos.index(repo) + 1} out of {repo_count}")

        # check if it exists in the M4_grading_temp folder
        if os.path.exists(f"M4_grading_temp/{repo.name}"):
            print(f"Repo {repo.name} already exists. Skipping")
            continue
            # skip = input(f"Repo {repo.name} already exists. Do you want to skip it? (y/n): ")
            # if skip == "y" or skip == "Y":
            #     continue  # skip it

        # if a test flag is passed, only grade repo called "module4-eddiejj13"
        # if test:
        #     if repo.name != repo_to_check:
        #         continue

        time.sleep(5)
        try:

            # wait for clicking the enter key before grading the next student
            input("Press enter to grade the next student")

            # create a new student object
            student = Student(repo.name, repo, g)
            # clone the student's repo
            student.clone_repo(clone)
            # replace the above with clone_from
            # clone the student's repo
            # student.clone_from(repo.clone_url)

            # put it in the error folder
            # move the repo to the "error" folder
            # move the repo to the error folder
            # create the error folder if it doesn't exist
            # if not os.path.exists("error"):
            #     os.makedirs("error")
            # # move the repo to the error folder
            # if not os.path.exists(f"error/{repo.name}"):
            #     # put it in the error folder
            #     shutil.move(f"M4_grading_temp/{repo.name}", f"error/{repo.name}")
            # continue to the next repo

            student.grade_all_regex()

            student.grade_all_baseball()

            student.edit_readme(student.tally_grades())

            # print the percentage of repos graded
            # clear the console
            # if not test:
            #     # on windows and on mac
            #     if os.name == "nt":
            #         os.system("cls")
            #     else:
            #         os.system("clear")
            #     print(f"{round((repos.index(repo) + 1) / repo_count * 100, 2)}% complete")

            # else:
            # exit("Grading complete.")
        except Exception as e:
            # move the repo to the "error" folder
            print(f"Error: {e}")
            # move the repo to the error folder
            # create the error folder if it doesn't exist
            if not os.path.exists("error"):
                os.makedirs("error")
            # move the repo to the error folder
            # if not already in the error folder
            if not os.path.exists(f"error/{repo.name}"):
                shutil.move(f"M4_grading_temp/{repo.name}", "error")
            # continue to the next repo
            continue


# if this file is run
if __name__ == "__main__":

    # get command line arguments using argparse
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", help="grade all repos", action="store_true")
    parser.add_argument("-t", "--test", help="test the autograder", action="store_true")
    parser.add_argument("-c", "--clone", help="clone repos", action="store_true")
    parser.add_argument("-i", "--individual", help="grade an individual repo <path to repo>")
    args = parser.parse_args()

    # if clone flag is set, set variable
    if args.clone:
        clone = True
        print("Cloning repos")
    else:
        clone = False

    # if test flag is set, set variable
    if args.test:
        test = True
    else:
        test = False

    if args.all:

        # if all flag is set, set variable
        run_autograder(clone, test)

    elif args.individual:
        #  get individual repo path from args
        individual_repo_path = args.individual
        print(individual_repo_path)
