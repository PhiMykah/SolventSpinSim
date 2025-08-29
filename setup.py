from setuptools import setup, find_packages

setup(
    name="solventspinsim",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "nmrPype",
        "dearpygui",
    ],
    entry_points={
        "console_scripts": [
            "solventspinsim = solventspinsim.main:main",
        ]
    },
    author="Micah Smith",
    author_email="mykahsmith21@gmail.com",
    description="",
)
