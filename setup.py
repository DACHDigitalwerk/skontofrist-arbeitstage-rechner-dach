# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="skontofrist-dach",
    version="1.0.0",
    description="DACH Skontofrist-, Zahlungsziel- & Bankarbeitstage-Rechner 2026",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="DACH Digitalwerk",
    author_email="dach.digitalwerk@gmail.com",
    url="https://github.com/DACHDigitalwerk/skontofrist-arbeitstage-rechner-dach",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "dach-skontofrist=skontofrist_dach.cli:main",
        ],
    },
)
