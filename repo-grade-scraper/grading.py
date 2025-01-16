import json
import argparse
import os
import subprocess
import re
import csv
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager


def load_repos_from_json(module_file):
    try:
        with open(module_file, 'r') as file:
            data = json.load(file)
        repos = [entry['repo'] for entry in data]
        return repos
    except FileNotFoundError:
        print(f"[ERROR]: Module file '{module_file}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR]: Failed to parse JSON in '{module_file}': {e}")
        return []

def get_readme_content(repo_path):
    readme_path = os.path.join(repo_path, "README.md")
    try:
        with open(readme_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"[ERROR]: README.md not found in {repo_path}.")
        return None

def find_grade_in_readme(readme_content):
    total_earned, total_possible, student_id = None, None, None
    lines = readme_content.splitlines()
    for i, line in enumerate(lines):
        if "Total Earned" in line and i + 2 < len(lines):
            data_line = lines[i + 2].split('|')
            if len(data_line) >= 3:
                total_earned = data_line[1].strip()
                total_possible = data_line[2].strip()
        if not student_id:
            match = re.search(r"\b\d{6}\b", line)
            if match:
                student_id = match.group()
    return total_earned, total_possible, student_id

def process_repo(repo_name, git_base_url, results):
    full_repo_url = f"{git_base_url}{repo_name}"
    repo_path = f"./temporary-repo-directory/{repo_name}"

    subprocess.run(["git", "clone", full_repo_url, repo_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "-C", repo_path, "checkout", "grading"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    readme_content = get_readme_content(repo_path)
    if readme_content:
        total_earned, total_possible, student_id = find_grade_in_readme(readme_content)
        if total_earned and total_possible and student_id:
            grade = round(float(total_earned) / float(total_possible) * 100, 2)
            results.append([student_id, total_earned, total_possible, grade])
            print(f"[SUCCESS]: Exported grade for {student_id} - {grade}%")
        else:
            print(f"\n[FAILURE]: Could not parse grades for {repo_name}. Check this repo out Mr. Zach Man: {full_repo_url}. I bet you the grader didn't use the template.\n")
    else:
        print(f"[ERROR]: README.md not found in {repo_name}.")

    subprocess.run(["rm", "-rf", repo_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    parser = argparse.ArgumentParser(description='Parallelize repo grading.')
    parser.add_argument('org_name', help='The organization name for repos.')
    parser.add_argument('module_number', help='The module number.')
    args = parser.parse_args()

    module_file = f"./util/json-files/module-{args.module_number}.json"
    repos = load_repos_from_json(module_file)
    if not repos:
        print("[ERROR]: No repos found.")
        return

    print(f"Processing {len(repos)} repos...")

    git_base_url = f"https://github.com/{args.org_name}/"
    os.makedirs("grades", exist_ok=True)
    csv_file_path = f"grades/module-{args.module_number}-grades.csv"

    with Manager() as manager:
        results = manager.list()
        with ThreadPoolExecutor() as executor:
            executor.map(lambda repo: process_repo(repo, git_base_url, results), repos)

        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Student ID", "Total Earned", "Total Possible", "Grade (%)"])
            csv_writer.writerows(results)

    print(f"[DONE]: Grades saved to '{csv_file_path}'.")

if __name__ == "__main__":
    main()
