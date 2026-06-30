#!/usr/bin/env python3
"""
Setup script for Locust Performance Testing Framework
"""

from setuptools import setup, find_packages
import os

# Read README for long description
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(current_dir, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f.readlines() 
                   if line.strip() and not line.startswith("#")]

setup(
    name="locust-performance-testing-framework",
    version="1.0.0",
    description="Comprehensive Locust-based performance testing framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    author="Demo Framework",
    author_email="demo@example.com",
    url="https://github.com/demo/locust-performance-testing-framework",
    
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.yaml", "*.yml", "*.csv"],
        "data": ["*.csv", "*.json"],
        "config": ["*.py", "*.json", "*.yaml"],
        "templates": ["*.html", "*.j2"],
    },
    
    install_requires=requirements,
    
    python_requires=">=3.8",
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Benchmark",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
    ],
    
    keywords="performance testing, load testing, stress testing, locust, automation, api testing",
    
    entry_points={
        "console_scripts": [
            "locust-runner=run_tests:main",
            "locust-framework=run_tests:main",
        ],
    },
    
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-html>=3.2.0",
            "pytest-xdist>=3.3.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "grafana-api>=1.0.0",
            "influxdb>=5.3.0",
        ],
        "database": [
            "psycopg2-binary>=2.9.0",
            "pymongo>=4.5.0",
            "redis>=5.0.0",
            "sqlalchemy>=2.0.0",
        ],
        "cloud": [
            "boto3>=1.28.0",
            "azure-storage-blob>=12.17.0",
            "google-cloud-storage>=2.10.0",
        ],
    },
    
    project_urls={
        "Bug Reports": "https://github.com/demo/locust-performance-testing-framework/issues",
        "Source": "https://github.com/demo/locust-performance-testing-framework",
        "Documentation": "https://locust-framework.readthedocs.io/",
    },
    
    zip_safe=False,
) 