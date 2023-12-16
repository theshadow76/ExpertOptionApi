from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ExpertOptionAPI',
    version='0.5',
    packages=find_packages(where="./"),
    package_dir={'': "./"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        # list your package dependencies here
        "websocket",
        "simplejson",
        "pandas"
    ],
)
