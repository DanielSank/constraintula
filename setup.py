# Copyright 2020 The constraintula Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import setuptools


README_FILENAME = "README.md"
VERSION_FILENAME = "constraintula/__init__.py"
VERSION_RE = r"^__version__ = ['\"]([^'\"]*)['\"]"


# Get version information
with open(VERSION_FILENAME, "rt") as version_file:
    mo = re.search(VERSION_RE, version_file.read(), re.M)

if mo:
    version = mo.group(1)
else:
    msg = "Unable to find version string in %s." % (version_file,)
    raise RuntimeError(msg)

# Get description information
with open(README_FILENAME, "rt") as description_file:
    long_description = description_file.read()


requirements = [
    'attr',
    'numpy',
    'sympy',
    'typing',
]

setuptools.setup(
    name='constraintula',
    version=version,
    author='Daniel Sank',
    author_email='sank.daniel@gmail.com',
    description='Define system of constraint equations for initializing data classes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/DanielSank/constraintula',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
