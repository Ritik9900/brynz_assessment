from setuptools import setup, find_packages

setup(
    name="property-capture",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "open3d>=0.18.0",
        "torch>=2.2.0",
        "shapely>=2.0.0",
        "gtsam>=4.2.0",
        "pydantic>=2.5.0",
        "scipy>=1.12.0"
    ],
    entry_points={
        "console_scripts": [
            "run_pipeline=run_pipeline:main",
        ]
    }
)
