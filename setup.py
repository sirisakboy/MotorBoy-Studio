from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hondaecu",
    version="1.0.0",
    author="MCU Innovations Inc",
    author_email="info@mcuinnovations.com",
    description="A diagnostic and flashing tool for Honda ECUs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RyanHope/HondaECU",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Automotive",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyusb",
        "pydispatcher",
        "wxPython",
        "requests",
        "lxml",
        "numpy>=1.20",
        "colour",
        "pyparsing",
        "gitpython",
        "appdirs",
    ],
    extras_require={
        "dev": [
            "pyinstaller",
        ],
    },
    entry_points={
        "console_scripts": [
            "hondaecu=HondaECU.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["images/*.png", "images/*.ico"],
    },
)