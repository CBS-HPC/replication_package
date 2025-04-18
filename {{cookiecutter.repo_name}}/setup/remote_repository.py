import os
import subprocess

from utils import *
from readme_templates import *
from get_dependencies import get_setup_dependencies
from update_requirements import update_requirements

def setup_remote_repository(version_control,code_repo,repo_name,description):
    """Handle repository creation and log-in based on selected platform."""

    # Change Dir to project_root
    os.chdir(str(pathlib.Path(__file__).resolve().parent.parent))

    if version_control == None or not os.path.isdir(".git"):
        return False
    if code_repo and code_repo.lower() == "github":
        flag = install_gh("./bin/gh")     
    elif code_repo and code_repo.lower() == "gitlab":
        flag  = install_glab("./bin/glab")
    else:
        return False 
    if flag:    
        flag = setup_repo(version_control,code_repo,repo_name,description) 
    if not flag:
        save_to_env("None","CODE_REPO",".cookiecutter")
    return flag

def install_py_package():

    # Change the current working directory to to setup folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run "pip install -e ."
    result = subprocess.run(['pip', 'install', '-e', '.'], capture_output=True, text=True)

    if result.returncode == 0:
        print("Installation successful.")
    else:
        print(f"Error during installation: {result.stderr}")

@ensure_correct_kernel
def main():
    version_control = load_from_env("VERSION_CONTROL",".cookiecutter")
    repo_name = load_from_env("REPO_NAME",".cookiecutter")
    code_repo = load_from_env("CODE_REPO",".cookiecutter")
    project_description = load_from_env("PROJECT_DESCRIPTION",".cookiecutter")
    python_env_manager = load_from_env("PYTHON_ENV_MANAGER",".cookiecutter")

    # Create Remote Repository
    flag = setup_remote_repository(version_control,code_repo,repo_name,project_description)

    install_cmd = load_from_env("INSTALL_CMD",".cookiecutter")
    requirements_file = load_from_env("REQUIREMENT_FILE",".cookiecutter")

    if requirements_file == "requirements.txt":
        create_requirements_txt(requirements_file)
    elif requirements_file == "environment.yml": 
        export_conda_env(repo_name)

    folder = str(pathlib.Path(__file__).resolve().parent.parent / pathlib.Path("./setup/"))
    file = str(pathlib.Path(__file__).resolve().parent.parent / pathlib.Path("./setup/dependencies.txt"))
    requirements_file  = str(pathlib.Path(__file__).resolve().parent.parent / pathlib.Path(requirements_file))

    # Updating requirements.txt/environment.yaml  # FIX ME
    if python_env_manager.lower() in ["conda","venv"]:
        get_setup_dependencies(folder_path = folder, file_name = file , requirements_file = requirements_file,install_cmd = install_cmd)
        push_msg = f"'{requirements_file}' and '{file}' created and 'Requirements' section in README.md updated"
    else:
        get_setup_dependencies(folder_path = folder, file_name = file, requirements_file = None,install_cmd = None)
        push_msg = "requirements.txt created"

    update_requirements(dependencies_files = [file], sections= ["setup"])

    # Pushing to Git 
    git_push(flag,push_msg)

    # Installing package:
    install_py_package()

if __name__ == "__main__":
    main()