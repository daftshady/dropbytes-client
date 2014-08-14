import dropbytes

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=dropbytes.__title__,
    version=dropbytes.__version__,
    url='https://github.com/daftshady/dropbytes-client/',
    author=dropbytes.__author__,
    author_email='daftonshady@gmail.com',
    license=dropbytes.__license__,
    packages=[
        'dropbytes'
    ],
    scripts=[
        'bin/dropbytes'
    ]
)
