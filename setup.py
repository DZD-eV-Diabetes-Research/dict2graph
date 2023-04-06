from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="dict2graph",
    description="Class to extract, transform and load (ETL) dicts/json to a Neo4j graph",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://dzd-ev.github.io/dict2graph-docs/",
        "Source": "https://github.com/DZD-eV-Diabetes-Research/dict2graph",
        "Tracker": "https://github.com/DZD-eV-Diabetes-Research/dict2graph/issues",
    },
    url="https://dzd-ev.github.io/dict2graph-docs/",
    author="Tim Bleimehl",
    author_email="tim.bleimehl@helmholtz-munich.de",
    license="MIT",
    packages=["dict2graph"],
    install_requires=[
        "py2neo",
        "neo4j",
        "graphio",
    ],
    extras_require={
        "tests": ["pytest", "deepdiff"],
        "docs": [
            "mkdocs",
            "mkdocstrings[python]",
            "mkdocs-autorefs",
            "mkdocs-material",
        ],
    },
    python_requires=">=3.9",
    zip_safe=False,
    include_package_data=True,
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        # "local_scheme": "node-and-timestamp"
        "local_scheme": "no-local-version",
        "write_to": "version.py",
    },
    setup_requires=["setuptools_scm"],
)
