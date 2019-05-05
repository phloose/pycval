from setuptools import setup, find_packages

setup(
    name="PyCVal",
    packages=['pycval'],
    version='0.1.0',
    entry_points = {
        'console_scripts': [
            'pycval = pycval.__main__:main'
        ]
    }
)
