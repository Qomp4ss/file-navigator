from setuptools import setup, find_packages
from .file_navigator.__init__ import __version__

setup(
    name="file-navigator",
    description="Flexible directory scanner, file path manager, and customizable file loader—all in one",
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown",
    version=__version__,
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