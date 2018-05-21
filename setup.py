from setuptools import setup, find_packages

setup(
    name='reply_card_corrector',
    version='0.1.0',
    packages=find_packages(),

    author='Thiago Sant Helena',
    author_email='thiago.sant.helena@gmail.com',

    license='MIT',

    install_requires=[opencv-python, numpy],
)
