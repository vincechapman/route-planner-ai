from setuptools import find_packages, setup
from route_finder import __version__

setup(
    name='route_finder',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)