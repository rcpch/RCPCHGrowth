from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rcpchgrowth",
    version="4.3.1",
    description="SDS and Centile calculations for UK Growth Data",
    long_description=long_description,
    url="https://github.com/rcpch/digital-growth-charts/blob/master/README.md",
    author="@eatyourpeas, @marcusbaw, @statist7, RCPCH Incubator",
    author_email="incubator@rcpch.ac.uk",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    keywords="growth charts, anthropometry, SDS, centile, UK-WHO, UK90, Trisomy 21 (UK), Trisomy 21 (AAP), Turner, CDC",
    packages=find_packages(),
    python_requires=">3.8",
    install_requires=["python-dateutil", "scipy"],
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/rcpch/rcpchgrowth-python/issues",
        "API management": "https://dev.rcpch.ac.uk",
        "Source": "https://github.com/rcpch/rcpchgrowth-python",
    },
)
