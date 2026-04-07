"""Setup configuration for warehouse_env."""

from setuptools import setup, find_packages

setup(
    name="warehouse-env",
    version="1.0.0",
    description="Real-world warehouse inventory management RL environment",
    author="OpenEnv Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0",
        "numpy>=1.24",
        "fastapi>=0.100",
        "uvicorn>=0.23",
        "openai>=1.0",
        "python-dotenv>=1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
        ],
    },
)
