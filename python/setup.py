"""Setup for choptyuk-spinor Python package."""

from setuptools import setup, find_packages

setup(
    name="choptyuk-spinor",
    version="1.0.0",
    author="Ishak Khamzatovich Isaev",
    author_email="aslan08_05@mail.ru",
    url="https://github.com/wild8highlander/choptuik_ac_bc",
    license="Isaev Proprietary License",
    description="Verification and simulation of spinor corrections b-C and a-C on the Klein quartic curve",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "matplotlib>=3.7",
        "mpmath>=1.3",
    ],
    extras_require={
        "reports": ["python-docx>=0.8.11", "reportlab>=4.0", "jinja2>=3.1"],
        "all": ["python-docx>=0.8.11", "reportlab>=4.0", "jinja2>=3.1", "markdown>=3.4"],
    },
)
