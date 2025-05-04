from setuptools import setup, find_packages

setup(
    name="herpai-ingestion",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "dynaconf",
        "aiohttp",
    ],
    entry_points={
        "console_scripts": [
            "herpai=herpai_ingestion.cli:cli",
        ],
    },
) 