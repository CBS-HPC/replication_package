#!/bin/bash

# List of applications to check in .env
APPS=()

# Check for specific folders and adjust the APPS list
if [ -d ".datalad" ]; then
    APPS=("GIT" "CONDA" "GH" "GLAB" "GIT-ANNEX" "DATALAD" "RCLONE" "GIT-ANNEX-REMOTE-RCLONE")
elif [ -d ".dvc" ]; then
    APPS=("GIT" "CONDA" "GH" "GLAB" "DVC")
elif [ -d ".git" ]; then
    APPS=("GIT" "CONDA" "GH" "GLAB")
else
    APPS=("CONDA")
fi

# Check if the .env file exists in the current folder
if [ -f ".env" ]; then
    echo ".env file found."

    # Iterate over the list of applications
    for app in "${APPS[@]}"; do
        # Use grep to check if the line for the app exists
        line=$(grep -E "^${app}=" .env)
        if [ -n "$line" ]; then
            # Extract the value and set it as an environment variable
            value=$(echo "$line" | cut -d'=' -f2 | tr -d '"')
            #value=$(dirname "$value")
            export PATH="$value:$PATH"

            # Set the environment variable persistently for the user (for future sessions)
            echo "export $app=\"$value\"" >> ~/.bashrc
        else
            echo "$app not found in .env."
        fi
    done

    # Check if Conda is in the path
    if ! command -v conda &> /dev/null; then
        echo "Conda is not found in the path. Please ensure Conda is installed and in the path."
        exit 1
    else
        echo "Conda is available in the path."
        # Initiate Conda and reboot 
        conda init && bash -i    
    fi

    # Attempt to activate the Conda environment
    FOLDER_NAME=$(basename "$PWD")

    # Try to activate Conda environment
    {
        echo "Attempting to activate Conda environment '$FOLDER_NAME'..."
        conda activate "$FOLDER_NAME" || { echo "Failed to activate Conda environment '$FOLDER_NAME'."; exit 1; }
    } || {
        # Catch block: Handle errors
        echo "Failed to activate Conda environment '$FOLDER_NAME'."

        # Check if environment.yml exists and create the environment
        if [ -f "environment.yml" ]; then
            echo "Found environment.yml. Creating Conda environment..."
            conda env create -f environment.yml || { echo "Failed to create Conda environment."; exit 1; }
            echo "Conda environment created. Activating..."
            conda activate "$FOLDER_NAME" || { echo "Failed to activate Conda environment after creation."; exit 1; }
        else
            echo "No Conda environment named '$FOLDER_NAME' and no environment.yml found."
            exit 1
        fi
    }

else
    echo "No .env file found in the current folder."
    exit 1
fi