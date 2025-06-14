from setuptools import setup, find_packages

setup(
    name='setup',
    version='1.0',
    packages=find_packages(where="."),
    package_dir={'': '.'},
    entry_points={
        'console_scripts': [
            'push-backup=utils.backup_tools:push_backup',
            'set-dataset=utils.set_dataset:main',
            'update-dependencies=utils.get_dependencies:main',
            'install-dependencies=utils.install_dependencies:main',
            'deic-storage-download=utils.deic_storage_download:main',
            'update-readme=utils.readme_templates:main',
            'reset-templates=utils.code_templates:main',
            'code-examples=utils.example_templates:main',
            'git-config=utils.repo_tools:main',
            'ci-control=utils.ci_tools:ci_control'


        ],
    },
    install_requires=[
        'python-dotenv',
        'pyyaml',
        'requests',
        'nbformat',
        'beautifulsoup4',
    ],
)