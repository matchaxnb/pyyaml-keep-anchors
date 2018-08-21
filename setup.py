from setuptools import setup, find_packages

setup(
    name='pyyaml-keep-anchors',
    description='Keep anchor references when parsing yaml files',

    version='1.0',

    packages=find_packages('.'),
    install_requires=[
        'PyYAML'
    ]
)
