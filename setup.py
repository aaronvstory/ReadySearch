"""Setup script for ReadySearch automation."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="readysearch-automation",
    version="1.0.0",
    author="ReadySearch Automation",
    description="Automated name searching and matching for ReadySearch.com.au",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "playwright>=1.40.0",
        "pandas>=2.1.4",
        "asyncio-throttle>=1.0.2",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "readysearch-automation=main:main",
        ],
    },
)