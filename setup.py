from setuptools import setup, find_packages

setup(
    name='reply_card_corrector',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points='''
        [console_scripts]
        reply-card-corrector=reply_card_corrector.__main__:main
    ''',
)
