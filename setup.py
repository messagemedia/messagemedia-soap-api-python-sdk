"""
Package configuration file
"""
from setuptools import find_packages, setup

setup(
    name='MMSoap',
    packages=find_packages(),
    url='https://github.com/infoxchange/messagemedia-python',
    license='Apache',
    description='This library provides a simple interface for sending and receiving messages using the MessageMedia SOAP API.',
    long_description=open('README.md').read(),
    install_requires=[
        "suds",
    ],
    tests_require=[
    ],
)
