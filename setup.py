"""
Setup file untuk proyek Forecast Vibecoding
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="forecast-vibecoding",
    version="1.0.0",
    author="Vibecoding Team",
    author_email="team@vibecoding.com",
    description="Aplikasi forecasting harga cryptocurrency menggunakan model Prophet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/forecast-vibecoding",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "forecast-app=src.views.app:main",
        ],
    },
)