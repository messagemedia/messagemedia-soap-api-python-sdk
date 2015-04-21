"""
Package configuration file
"""
from setuptools import find_packages, setup

setup(
    name='MMSoap',
    packages=find_packages(),
    url='https://github.com/messagemedia/messagemedia-python',
    license='Apache',
    description='This library provides a simple interface for sending and receiving messages using the MessageMedia SOAP API.',
    long_description=open('README.md').read(),
    install_requires=[
        "suds==0.4.0",
    ],
    tests_require=[
    ],
)
