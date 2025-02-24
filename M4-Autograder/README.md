# M4 Autograder

## Usage

```
python main.py <github_org_name> <name_of_repo_template>
```

- The `github_org_name` is something like cse330-spring-2025
-  `name_of_repo_template` is the name of the repo from which every repo for the given assignment was forked. Each assignment (e.g., module 2 group) has its own template repo.

## Output
Results are written to a CSV file `m4_autograder_results.csv` containing Student ID, Grade, and Repo Link. If a student ID can't be found, it will default to `000000`

## Ollama
90% of the assignment is autograded by plain old python logic. However! The four points for a clear and appropriate usage message are more difficult to autograde. To solve this issue, the script sends the usage message to a local LLM based on `qwen2.5:0.5b` with a special system prompt. This model is run with Ollama (see installation below) and built with the [Modelfile](./LLM/Modelfile) provided.

## installation
```bash
# make ./setup.sh executable
chmod +x setup.sh
```

Before continuing, make sure you have Ollama installed.
```
# run the setup script. This will install python packages and setup the Ollama model
./setup.sh

```
