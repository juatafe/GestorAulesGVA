#!/usr/bin/env python3
# =============================================================================
# setup.py - Configuració per a PyInstaller i distribució
# =============================================================================

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="gestor_aules_gva",
    version="2.0.0",
    author="jbtalens",
    author_email="tu@email.com",
    description="Gestor per a importar escales i crear outcomes a Aules GVA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/gestor_aules_gva",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gestor-aules-gva=gestor_aules_gva.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gestor_aules_gva": ["../icons/*.png", "../icons/*.ico"],
    },
    # Afegeix això al setup.py
    package_data={
        "gestor_aules_gva": [
            "../icons/*.png", 
            "../icons/*.ico",
            "../GestorAulesGVA.desktop"
        ],
    },
    data_files=[
        ('share/applications', ['GestorAulesGVA.desktop']),
        ('share/icons', ['icons/gestor-aules.png']),
    ]
)