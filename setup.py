"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import os

from setuptools import setup, find_packages

# pylint: disable=redefined-builtin

here = os.path.abspath(os.path.dirname(__file__))  # pylint: disable=invalid-name

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()  # pylint: disable=invalid-name

setup(
    name='swagger_to',
    version='3.1.1',
    description='Generate server and client code from Swagger (OpenAPI 2.0) specification',
    long_description=long_description,
    url='https://github.com/Parquery/swagger-to',
    author='Marko Ristin',
    author_email='marko@parquery.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    license="License :: OSI Approved :: MIT License",
    keywords='swagger code generation python elm go typescript server client angular',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['pyyaml>=3.12', 'jinja2>=2.10,<3', 'icontract>=2.0.1,<3'],
    extras_require={'dev': [
        'mypy==0.560',
        'pylint==1.8.2',
        'yapf==0.20.2',
        'pydocstyle>=3.0.0,<4',
    ]},
    py_modules=['swagger_to'],
    package_data={"swagger_to": ["py.typed"]},
    scripts=[
        'bin/swagger_to_go_server.py', 'bin/swagger_to_py_client.py', 'bin/swagger_to_ts_angular5_client.py',
        'bin/swagger_to_elm_client.py', 'bin/swagger_style.py'
    ],
)
