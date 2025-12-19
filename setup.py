#!/usr/bin/env python3
"""
SynergyMesh Workflow System Setup
==================================

Production-ready workflow orchestration platform with AI governance,
multi-layer validation, and automated deployment capabilities.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements-workflow.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="machinenativeops-workflow",
    version="2.0.0",
    author="SynergyMesh Team",
    author_email="team@machinenativeops.io",
    description="Production-ready workflow orchestration platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MachineNativeOps/MachineNativeOps",
    project_urls={
        "Bug Reports": "https://github.com/MachineNativeOps/MachineNativeOps/issues",
        "Source": "https://github.com/MachineNativeOps/MachineNativeOps",
        "Documentation": "https://github.com/MachineNativeOps/MachineNativeOps/tree/main/docs",
    },
    packages=find_packages(include=["core", "core.*", "automation", "automation.*", "tools", "tools.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "machinenativeops-workflow=automation.pipelines.instant_execution_pipeline:main",
            "machinenativeops-contract=core.contract_engine:main",
            "machinenativeops-generate-contract=tools.generators.contract_generator:main",
            "machinenativeops-generate-validator=tools.generators.validator_generator:main",
            "machinenativeops-generate-docs=tools.generators.documentation_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    zip_safe=False,
)
