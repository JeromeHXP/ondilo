import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ondilo",
    version="0.4.0",
    author="Jérôme Mainguet",
    author_email="dartdoka@mainguet.fr",
    description="A client to access Ondilo ICO APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JeromeHXP/ondilo",
    packages=setuptools.find_packages('src'),
    package_dir={"": "src"},
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["requests", "requests_oauthlib", "oauthlib"],
)
