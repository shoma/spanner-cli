from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

about = {}

with open(path.join(here, "spannercli", "__init__.py")) as f:
    exec(f.read(), about)

setup(
    name="spanner-cli",
    version=about["__version__"],
    url="https://github.com/shoma/spanner-cli",
    packages=find_packages(exclude=["tests", "tests.*", "tasks", "tasks.*"]),
    entry_points={
        "console_scripts": [
            "spanner-cli=spannercli:main.main",
        ]
    },
    python_requires=">=3.6",
    setup_requires=[],
    include_package_data=True,
)
