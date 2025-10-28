"""
Setup script for autopro-common shared library
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autopro-common",
    version="1.0.0",
    author="AutoPro Daune Team",
    description="Shared utilities for AutoPro microservices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.27.0",
        "sqlalchemy[asyncio]>=2.0.0",
        "asyncpg>=0.29.0",
        "redis[hiredis]>=5.0.0",
        "aio-pika>=9.3.0",
        "prometheus-client>=0.19.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
