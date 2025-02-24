# Parse Grades from Repos Script

## Running

```bash
python3 get_grades_from_repos.py <module_number> <group_or_individual> <org_name>
```

where:

-   `module_number` is the module that you want to push grading templates to.
-   `group_or_individual` will take value "individual" or "group". This will specify if the script pushes for the individual gradin teplate of that module or the group of it.
-   `org_name` is the name of this semesters organization. Specifically, you can find it in the git url for all of the student repos like: `https://github.com/<org_name>/`. For example, `https://github.com/cse330-fall-2024/` would have an org_name of cse330-fall-2024
-  `name_of_repo_template` is the name of the repo from which every repo for the given assignment was forked. Each assignment (e.g., module 2 group) has its own template repo.

The output will map student id's to grades and can be found in `repo-grade-scraper/results`

---

If you have any questions, feel free to reach out to [Jayce Bordelon](https://jaycebordelon.netlify.app):

-   Email: <b.jayce@wustl.edu>

-   Phone: (832)-260-5650
