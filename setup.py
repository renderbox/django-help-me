# --------------------------------------------
# Copyright 2019, Grant Viklund
# @Author: Grant Viklund
# @Date:   2019-08-06 15:10:20
# --------------------------------------------

from os import path
from setuptools import setup, find_packages

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')

try:
    from m2r import parse_from_file
    long_description = parse_from_file(readme_file)     # Convert the file to RST for PyPI
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()


package_metadata = {
    'name': 'django-help-me',
    'version': '0.1.3',
    'description': 'A simple app for providing a simple help desk for users.',
    'long_description': long_description,
    'url': 'https://github.com/renderbox/django-help-me/',
    'author': 'Grant Viklund',
    'author_email': 'renderbox@example.com',
    'license': 'MIT license',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    'keywords': ['django', 'app'],
}

setup(
    **package_metadata,
    packages=find_packages(),
    package_data={'helpme': ['templates/helpme/*.html', 'static/js/support/*.js']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'Django>=3.1, <3.2',
        'django-autoslug',
        'django-extensions',
        'django-crispy-forms',
    ],
    extras_require={
        'dev': [
            'django-allauth',
            'dj-database-url',
            'psycopg2-binary',
            'ipython',
            'pylint',
            'djangorestframework',
            'django-multiselectfield',
        ],
        'test': [],
        'prod': [],
        'build': [
            'setuptools',
            'wheel',
            'twine',
            'm2r',
        ],
        'docs': [
            'coverage',
            'Sphinx',
            'sphinx-bootstrap-theme',
            'sphinx-rtd-theme',
            'sphinx-js',
            'm2r',
        ],
    }
)
