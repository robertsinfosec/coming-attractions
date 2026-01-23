"""Setup configuration for coming-attractions package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="coming-attractions",
    version="1.0.0",
    author="robertsinfosec",
    author_email="",
    description="Automated Jellyfin Upcoming Movie Trailer Management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robertsinfosec/coming-attractions",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "coming-attractions=coming_attractions.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
