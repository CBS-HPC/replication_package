# PowerShell script to set up environment and run specified Python scripts

# Get parameters passed from PowerShell
param (
    [string]$repo_name,
    [string]$env_manager,  # Environment manager: Conda, venv, or virtualenv
    [string]$version_control_path,
    [string]$remote_repository_path
)

# Activate environment based on the environment manager
if ($repo_name -ne "None") {
    switch ($env_manager.ToLower()) {
        "conda" {
            Write-Output "Activating Conda environment: $repo_name"
            conda activate $repo_name
        }
        "venv" {
            Write-Output "Activating venv environment: $repo_name"
            $venv_activate = "./$repo_name/Scripts/activate"  # For Windows

            if (Test-Path $venv_activate) {
                Write-Output "Activating venv using $venv_activate"
                & $venv_activate
            } else {
                Write-Output "Error: venv activation script not found."
            }
        }
        "virtualenv" {
            Write-Output "Activating virtualenv environment: $repo_name"
            $virtualenv_activate = "./$repo_name/Scripts/activate"  # For Windows

            if (Test-Path $virtualenv_activate) {
                Write-Output "Activating virtualenv using $virtualenv_activate"
                & $virtualenv_activate
            } else {
                Write-Output "Error: virtualenv activation script not found."
            }
        }
        default {
            Write-Output "Error: Unsupported environment manager '$env_manager'. Supported values are: Conda, venv, virtualenv."
        }
    }
} else {
    Write-Output "No repo_name provided. Skipping environment activation."
}

# Check if the script paths are provided and run them
if (Test-Path $version_control_path) {
    Write-Output "Running version_control.py from $version_control_path..."
    python $version_control_path
} else {
    Write-Output "Error: $version_control_path not found."
}

if (Test-Path $remote_repository_path) {
    Write-Output "Running remote_repository.py from $remote_repository_path..."
    python $remote_repository_path
} else {
    Write-Output "Error: $remote_repository_path not found."
}

Write-Output "Environment setup completed successfully."