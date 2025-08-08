"""
HoneyNet Setup Script
סקריפט התקנה של HoneyNet
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements file
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="honeynet-global",
    version="2.0.0",
    description="HoneyNet - Global Multilingual Cyber Defense Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HoneyNet Global Team",
    author_email="info@honeynet.global",
    url="https://github.com/honeynet/honeynet-global",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Operating System :: OS Independent",
        "Natural Language :: Hebrew",
        "Natural Language :: English",
        "Natural Language :: Arabic",
        "Natural Language :: Spanish",
        "Natural Language :: French",
        "Natural Language :: German",
        "Natural Language :: Russian",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: Japanese",
        "Natural Language :: Korean",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "cryptography>=41.0.0",
        "psutil>=5.9.0",
        "aiofiles>=23.0.0",
        "python-multipart>=0.0.6",
        "websockets>=11.0",
        "asyncio-mqtt>=0.13.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "requests>=2.31.0",
        "Pillow>=10.0.0",
        "qrcode[pil]>=7.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "server": [
            "redis>=5.0.0",
            "asyncpg>=0.28.0",
            "sqlalchemy>=2.0.0",
        ],
        "desktop": [
            "tkinter",
            "customtkinter>=5.2.0",
        ],
        "mobile": [
            "kivy>=2.2.0",
            "kivymd>=1.1.0",
        ],
        "cloud": [
            "boto3>=1.28.0",
            "azure-storage-blob>=12.17.0",
            "google-cloud-storage>=2.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "honeynet-server=server.main:main",
            "honeynet-desktop=launch_desktop:main",
            "honeynet-demo=demo:main",
            "honeynet-install=scripts.installer:main",
            "honeynet-build=scripts.builder:main",
        ],
        "gui_scripts": [
            "HoneyNet=launch_desktop:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.ico", "*.png", "*.jpg"],
        "i18n": ["languages/*.json"],
        "assets": ["icons/*", "images/*"],
        "scripts": ["*.bat", "*.sh", "*.ps1"],
    },
    data_files=[
        ('share/applications', ['assets/honeynet.desktop']),
        ('share/icons/hicolor/256x256/apps', ['assets/icons/honeynet.png']),
    ],
    zip_safe=False,
        "Documentation": "https://docs.honeynet.com",
        "Funding": "https://github.com/sponsors/honeynet",
    },
)
