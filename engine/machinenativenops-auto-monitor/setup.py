#!/usr/bin/env python3
"""
Setup script for MachineNativeOps Auto-Monitor
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="machinenativenops-auto-monitor",
    version="1.0.0",
    description="Autonomous monitoring and observability system for MachineNativeOps platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MachineNativeOps Platform Team",
    author_email="platform@machinenativeops.io",
    url="https://github.com/MachineNativeOps/machine-native-ops-aaps",
    project_urls={
        "Documentation": "https://docs.machinenativeops.io",
        "Source": "https://github.com/MachineNativeOps/machine-native-ops-aaps",
        "Tracker": "https://github.com/MachineNativeOps/machine-native-ops-aaps/issues",
    },
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "psutil>=5.9.0",
        "requests>=2.28.0",
        "PyYAML>=6.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "machinenativenops-auto-monitor=machinenativenops_auto_monitor.__main__:main",
        ],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Keywords
    keywords="monitoring observability metrics alerts machinenativeops autonomous",
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
)
