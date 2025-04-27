from setuptools import setup

setup(
    name='DomainGhost',
    version='1.0',
    scripts=['domain_ghost.py'],
    install_requires=[
        'requests',
        'colorama',
        'nmap',
        'whois',
    ],
)
