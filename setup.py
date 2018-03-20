from __future__ import (absolute_import, division, print_function)
import re
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
from configobj import ConfigObj


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as f:
    required = f.read().splitlines()
with open(os.path.join(here, "test_requirements.txt")) as f:
    test_requires = f.read().splitlines()

version_file = os.path.join(here, "mond_project", "_version.py")
verstrline = open(version_file, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    this_version = mo.group(1)
    print("mond_project version = ", this_version)
else:
    raise RuntimeError("Unable to find version string in %s" %(version_file))

class CustomInstall(install):
    user_options = install.user_options + [(str("api-key="), None, "The Illustris "\
            "API key, which will be set as the needed environment variable")]

    def initialize_options(self):
        self.api_key = None
        install.initialize_options(self)

    def finalize_options(self):
        install.finalize_options(self)

    def run(self):
        if self.api_key is not None:
            config = ConfigObj(os.path.join(here, "mond_project", 
                "mond_config.ini"))
            config["ILL_KEY"] = self.api_key
            config.write()
        install.run(self)

class CustomDevelop(develop):
    user_options = develop.user_options + [("api-key=", None, "The Illustris "\
            "API key, which will be set as the needed environment variable")]

    def initialize_options(self):
        develop.initialize_options(self)
        self.api_key = None

    def finalize_options(self):
        develop.finalize_options(self)

    def run(self):
        if self.api_key is not None:
            config = ConfigObj(os.path.join(here, "mond_project", 
                "mond_config.ini"))
            config["ILL_KEY"] = self.api_key
            config.write()
        develop.run(self)

setup(
        name="mond_project",
        version=this_version,
        description="Code for final project on MOND vs LCDM",
        url="https://github.com/wagoner47/mond_project/tree/master",
        packages=find_packages(exclude=["tests", "docs"]),
        setup_requires=["configobj", "pytest-runner"],
        install_requires=required,
        tests_require=test_requires,
        test_suite="nose2.collector.collector",
        python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
        cmdclass={"install":CustomInstall, "develop":CustomDevelop})
