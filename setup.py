from setuptools import setup, find_packages

VERSION = open('RAINLotus/v.py', encoding='utf-8')
README = open('README.md', encoding='utf-8')

setup(
    name='RAINLotus',
    author='20x48',
    author_email='the20x48@outlook.com',
    url='https://github.com/20x48/RAINLotus',
    version=VERSION.readline()[15:-2],
    packages=find_packages(),
    package_data={'RAINLotus': ['prism.min.css', 'rainink.min.css']},
    project_urls={'Github': 'https://github.com/20x48/RAINLotus'},
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'Topic :: Documentation',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    description='A -tranquilac- lightweight markup language with nearly 40 syntaxes.',
    long_description=README.read(),
    long_description_content_type='text/markdown'
)

VERSION.close()
README.close()