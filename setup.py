from PyGistApi import __author__, __license__, __version__, __url__, __description__
from setuptools import find_packages, setup


with open("./README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="PyGistApi",
    version=__version__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=__license__,
    author=__author__,
    author_email="YeahAmStark@gmail.com",
    url=__url__,
    keywords="github gist wrapper async sync",
    packages=find_packages(),
    install_requires=["httpx"],
    classifiers=[
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
