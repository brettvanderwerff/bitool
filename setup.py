import setuptools

description= 'A set of tools for working with torrent files and implementing the bit torrent protocol.'

with open("README.md", "r") as read_obj:
    long_description = read_obj.read()

setuptools.setup(
    name="bitool",
    version= "0.0.1",
    author="Brett Vanderwerff",
    author_email="brett.vanderwerff@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brettvanderwerff/bitool",
    packages=setuptools.find_packages(),
    install_requires=[
              'bencoder',
          ],
    classifiers=(
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
        ))