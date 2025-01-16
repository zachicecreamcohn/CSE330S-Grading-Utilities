# Push Grading Templates to Repos Script

## Running

To run this script, you will require a text file from professor sproull in the form similar to:

```txt
:module2-group-486661-518917:,DylanAlfonso13,
:module2-group-498593-497966:,JayceBordelon,
:module2-group-509213:,boncui,
:module2-group-511333-527024:,FortunaKadima,
...Other repos and graders
```

**Important** This file must be in the directory: `grading-template-to-repos/text-grader-mappings/module-<module_number>-<group_or_individual>.txt`

Then, to execute the appropriate push to the repos of a particular module, you will run:

```bash
python3 push_template_to_repos.py <module_number> <group_or_individual> <org_name>
```

where:

-   `module_number` is the module that you want to push grading templates to.
-   `group_or_individual` will take value "individual" or "group". This will specify if the script pushes for the individual gradin teplate of that module or the group of it.
-   `org_name` is the name of this semesters organization. Specifically, you can find it in the git url for all of the student repos like: `https://github.com/<org_name>/`. For example, `https://github.com/cse330-fall-2024/` would have an org_name of cse330-fall-2024
