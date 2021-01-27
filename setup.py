#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages  # type: ignore


extras_require = {
    "test": [
        "pytest>=6.0.1,<7",
        "pytest-xdist",
        "pytest-coverage",
    ],
    "lint": [
        "black==19.10b0",
        "flake8==3.8.4",
        "isort>=5.7.0,<6",
        "mypy==0.790",
        "pydocstyle>=5.1.1,<6",
    ],
    "doc": [
        "Sphinx>=3.4.3,<4",
        "sphinx_rtd_theme>=0.5.1",
    ],
    "dev": [
        "pytest-watch>=4.2.0,<5",
        "wheel",
        "twine",
        "ipython",
    ],
}

extras_require["dev"] = (
    extras_require["dev"]
    + extras_require["test"]  # noqa: W504
    + extras_require["lint"]  # noqa: W504
    + extras_require["doc"]  # noqa: W504
)

with open("./README.md") as readme:
    long_description = readme.read()

setup(
    name="ape-tokens",
    version="0.0.0a1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ApeWorX Ltd.",
    author_email="admin@apeworx.io",
    url="https://github.com/apeworx/ape-tokens",
    include_package_data=True,
    python_requires=">=3.6, <4",
    install_requires=["eth-brownie>=1.13.0,<2", "tokenlists<1.0"],
    extras_require=extras_require,
    py_modules=["ape_tokens"],
    license="Apache License 2.0",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
