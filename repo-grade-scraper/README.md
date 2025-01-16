# CSE 330 Grade Scraping Script Usage

## File conversion

I decided to make it so that the .txt file is converted to a json file (instead of a csv) to be used in the grading script.
You will find `./util/mappings_to_json.py` which will handle the file conversion.

**_Important:_** This is built such that the file structure is **Critical**. Any text files that come from Professor Sproull with the matching grader to repo name must be found in the directory/file format of `./util/text-files/module-<module_number>.txt`. Schematically, the files should follow an almost identical structure to:

```txt
:module1-1341524165:,gremaudm,
:module1-A3Bick:,DylanAlfonso13,
:module1-Aadarsha2002:,JayceBordelon,
:module1-AdamShumway04:,boncui,
:module1-AiboYu:,FortunaKadima,
:module1-AidinYazdiWUSTL:,Luncy-May,
:module1-Alec-T-A:,bhaktimalhotra21,
:module1-AndyHoette:,scarlettpatton,

Other Grades...
```

**Running the converter:** To convert this text file to the desired json format, you may run (from the **root directory** of the project):

```bash
## If you are in project root:
cd ./util && python3 mappings_to_json.py <module_number> && cd ..
## If you are in ./util, just run:
python3 mappings_to_json.py <module_number>
```

The `module_number` param will be whatever the file is named. For example: Lets say I have a file at `./util/text-files/module-1.txt`, then I would run `python3 ./util/mappings_to_json.py 1` to convert the file.

Once this is complete, you should see an equivalent filename under `./util/json-files/module-<module_number>.json` that follows the general schema of:

```json
[
    {
        "repo": "module1-1341524165",
        "grader": "gremaudm"
    },
    {
        "repo": "module1-A3Bick",
        "grader": "DylanAlfonso13"
    },
    {... Other repos}
]
```

## Running the grader

The actual grade scraper will take in two space seperated parameters:

1. **org_name**: This will be the name of the organization to scrape for the repos in any given semester. For example, if the base of the git url for this semester's repos is `https://github.com/cse330-fall-2024`, then the org_name would just be `cse330-fall-2024`
2. **module_number**: same as before. The module number will be the module of the assocated file for `./util/json-files/module-<module_number>.json`.

In summary running the script (from the root of this repo) will follow:

```bash
python3 grading.py <org_name> <module_number>
```

for example, if we had `module-1.json` for `cse330-fall-2024` org_name, we would run:

```bash
python3 grading.py cse330-fall-2024 1
```

## Running both simultaneously

If you are weird like me and want it all to magically happen with one command, run

```bash
cd util && python3 mappings_to_json.py <module_number> && cd .. && python3 grading.py <org_name> <module_number>
```

For Example:

```bash
cd util && python3 mappings_to_json.py 1 && cd .. && python3 grading.py cse330-fall-2024 1
```

Please note that this is not windows friendly (unless you are in bash) #nohate.

---

If you have any questions, feel free to reach out to [Jayce Bordelon](https://jaycebordelon.netlify.app):

-   Email: <b.jayce@wustl.edu>

-   Phone: (832)-260-5650
