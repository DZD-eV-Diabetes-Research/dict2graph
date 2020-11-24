from setuptools import setup

setup(
    name="dict2graph",
    version="0.4.3",
    description="Class to transfer json to a neo4j graph",
    url="",
    author="TB",
    author_email="tim.bleimehl@helmholtz-muenchen.de",
    license="MIT",
    packages=["dict2graph"],
    install_requires=[
        "py2neo",
        "graphio @ git+https://github.com/motey/graphio.git",
        "linetimer",
    ],
    zip_safe=False,
    include_package_data=True,
)
