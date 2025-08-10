"""Setup file for Agno Framework"""
from setuptools import setup, find_packages

setup(
    name="agno",
    version="0.1.0",
    description="Agno Framework - Lightweight AI Agent Framework for T-Developer",
    author="T-Developer Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.5.0",
        "aiohttp>=3.9.0",
        "redis>=5.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)