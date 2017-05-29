import re
from pathlib import Path
from setuptools import setup, find_packages

__all__ = (
    'read',
    'find_version'
)

__folder__ = Path(__file__).parent


def read(*path_leaves, **kwargs):
    kwargs.setdefault('encoding', "utf-8")
    with Path(__folder__, *path_leaves).open(**kwargs) as f:
        return f.read()


def find_version(*path_leaves):
    version_file = read(*path_leaves)
    version_match = re.search(r"^__version__ = (['\"])(.*?)\1", version_file, re.M)
    if version_match:
        return version_match.group(2)
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="st_package_reviewer",
    packages=find_packages(exclude=["tests"]),
    version=find_version("st_package_reviewer", "__init__.py"),
    description="Review Sublime Text packages",
    long_description=read("README.md"),
    url="https://github.com/packagecontrol/st_package_reviewer",
    author="FichteFoll",
    author_email="fichtefoll2@googlemail.com",
    license='MIT',
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=["sublime text", "review", ""],
    install_requires=read("requirements.in").splitlines(),
    package_data={
        # `data` directory contains reference .sublime-keymap files
        "st_package_reviewer": ["data/*", "README*"],
    },
    entry_points={
        'console_scripts': [
            "st_package_reviewer=st_package_reviewer.__main__:main",
        ],
    },
    zip_safe=False,
)
