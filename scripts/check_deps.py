#!/usr/bin/env python3
"""Check if all required dependencies are installed"""

import sys

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Run: pip install {package_name}")
        return False

print("Checking GoldMiner dependencies...\n")

dependencies = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn[standard]"),
    ("streamlit", "streamlit"),
    ("langchain", "langchain"),
    ("openai", "openai"),
    ("sqlalchemy", "sqlalchemy"),
    ("alembic", "alembic"),
    ("bs4", "beautifulsoup4"),
    ("selenium", "selenium"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("dotenv", "python-dotenv"),
    ("pydantic", "pydantic"),
    ("pydantic_settings", "pydantic-settings"),
    ("reportlab", "reportlab"),
    ("pypdf", "pypdf"),
    ("plotly", "plotly"),
    ("pytest", "pytest"),
    ("black", "black"),
    ("flake8", "flake8"),
]

all_good = True
for module, package in dependencies:
    if not check_import(module, package):
        all_good = False

if all_good:
    print("\n✨ All dependencies are installed!")
else:
    print("\n⚠️  Some dependencies are missing.")
    print("Run: pip install -r requirements.txt")

sys.exit(0 if all_good else 1)