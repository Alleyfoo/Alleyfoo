from setuptools import setup, find_packages

setup(
    name="toolbox",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="A collection of reusable Python utilities for data analysis and visualization.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # e.g. "pandas>=1.2.0", "matplotlib>=3.4.0", "seaborn>=0.11.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
