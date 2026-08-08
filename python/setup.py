from setuptools import setup, find_packages

setup(
    name="choptuik-ac-bc",
    version="2.0.0",
    author="Ishak Khamzatovich Isaev",
    description="Computational framework for spinor corrections on the Klein quartic curve",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
)
