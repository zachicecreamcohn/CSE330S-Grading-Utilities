#!/bin/bash

# NOTE: You will need Ollama installed to use this autograder

pip install -r requirements.txt
cd ./LLM/
chmod +x setup.sh
./setup.sh
cd ..
echo "Setup complete"
