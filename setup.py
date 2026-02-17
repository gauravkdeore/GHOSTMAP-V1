from setuptools import setup, find_packages

setup(
    name="ghostmap",
    version="1.0.0",
    description="GHOSTMAP — Discover undocumented (ghost) API endpoints and flag security risks",
    author="GHOSTMAP Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "tqdm>=4.65.0",
        "bleach>=6.0.0",
        "aiohttp>=3.9.0",
        "pyyaml>=6.0.0",
        "reportlab>=4.0.0",
        "streamlit>=1.30.0",
        "plotly>=5.18.0",
    ],
    entry_points={
        "console_scripts": [
            "ghostmap=ghostmap.cli:main",
        ],
    },
)
