import setuptools
import os

READ_ME_FILE = "README.md"
long_description = "Unable to load decription"
if os.path.exists(READ_ME_FILE):
    with open(READ_ME_FILE, "r") as fh:
        long_description = fh.read()

setuptools.setup(name="jimo_logservices-jimobama",
                 version="0.1.00000",
                 description="Native low level socket servers",
                 long_description=long_description,
                 url="http://192.168.0.12/jimobama/logingservices.git",
                 long_description_content_type="text/markdown",
                 author="Obaro I. Johnson",
                 author_email="johnson.obaro@hotmail.com",
                 packages=['jimo_logservices',],
                 install_requires=[
                     'events-jimobama @ git+https://github.com/miljimo/events.git@02e5be98bf50e65fc6c07089238aa16615853fa4'],
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",

                 ], python_requires='>=3.6')
