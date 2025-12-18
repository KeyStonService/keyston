"""Setup configuration for SynergyMesh Governance Framework"""
from setuptools import setup, find_packages
import os

# Read version from VERSION file
with open('VERSION', 'r') as f:
    version = f.read().strip()

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='synergymesh-governance',
    version=version,
    description='SynergyMesh 23-Dimension Enterprise Governance Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SynergyMesh Governance Team',
    author_email='governance-team@synergymesh.io',
    url=os.environ.get('REPOSITORY_URL', ''),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'governance-cli=governance.cli:main',
            'governance-dashboard=governance.dashboard:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
