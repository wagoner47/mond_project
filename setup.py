import re
from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as f:
    required = f.read().splitlines()

version_file = os.path.join(here, "mond_test", "_version.py")
verstrline = open(version_file, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    this_version = mo.group(1)
    print("mond_project version = ", this_version)
else:
    raise RuntimeError("Unable to find version string in %s" %(version_file))

setup(
        name="mond_project",
        version=this_version,
        description="Code for final project on MOND vs LCDM",
        url="https://github.com/wagoner47/mond_project/tree/master",
        packages=find_packages(exclude=["tests", "docs"]),
        install_requires=required)
