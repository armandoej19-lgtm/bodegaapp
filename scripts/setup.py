"""
Setup script for Bodega App
"""
from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="bodega-app",
    version="1.0.0",
    author="Tu Nombre",
    author_email="tu.email@example.com",
    description="Sistema de gestión de inventario para dispositivos electrónicos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/bodega-app",
    
    # Package discovery
    packages=find_packages(include=['src', 'src.*', 'config', 'models', 'views']),
    
    # Include data files
    package_data={
        '': ['*.txt', '*.md', '*.ini'],
        'config': ['*.py'],
        'data': ['*.db', 'exports/*', 'backups/*'],
    },
    
    # Dependencies
    install_requires=requirements,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points (crea comandos ejecutables)
    entry_points={
        'console_scripts': [
            'bodega-app=src.main:main',
            'bodega-import=scripts.import_data:main',
            'bodega-backup=scripts.backup_database:backup_database',
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Inventory",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Keywords
    keywords="inventory, bodega, devices, management, tkinter, sqlite",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/tuusuario/bodega-app/issues",
        "Source": "https://github.com/tuusuario/bodega-app",
        "Documentation": "https://github.com/tuusuario/bodega-app/docs",
    },
    
    # Additional requirements
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'gui': [
            'customtkinter>=5.2.0',
            'pillow>=10.0.0',
        ],
    },
    
    # Include non-Python files
    include_package_data=True,
    
    # Scripts
    scripts=[
        'scripts/setup.py',  # Tu script de configuración
        'scripts/backup_database.py',
        'scripts/import_data.py',
    ],
)