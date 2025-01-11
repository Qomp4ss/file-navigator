from setuptools import setup, find_packages
import os
import re

def find_version(file_path):
    """Extract the version string from the specified file."""
    with open(file_path, "r", encoding="utf-8") as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="file-navigator",
    description="Flexible directory scanner, file path manager, and customizable file loader—all in one",
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown",
    version=find_version("file_navigator/__init__.py"),
    license="MIT", 
    author="Qomp4ss",
    author_email="imaggine@gmail.com",
    maintainer="Qomp4ss",
    maintainer_email="imaggine@gmail.com",
    url="https://github.com/Qomp4ss/file-navigator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas>=0.22",
    ],
    keywords=["file", "flexible", "manager", "directory", "scanner", "path"],
    packages=find_packages(), 
)