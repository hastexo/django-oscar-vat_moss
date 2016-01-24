#!/usr/bin/env python
from setuptools import setup, find_packages

from oscar_vat_moss import get_version

setup(
    name='django-oscar-vat_moss',
    author='hastexo',
    author_email='code@hastexo.com',
    version=get_version(),
    url='https://github.com/hastexo/django-oscar-vat_moss',
    description=(
        "EU VATMOSS support for django-oscar"),
    long_description=open('README.rst').read(),
    keywords="VATMOSS, Tax, Oscar",
    license=open('LICENSE').read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'requests>=1.0',
        'django-localflavor'],
    extras_require={
        'oscar': ["django-oscar>=1.1"]
    },
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Other/Nonlisted Topic'],
)
