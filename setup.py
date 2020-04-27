from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as README:
    setup(
        name='RAINLotus',
        author='20x48',
        author_email='the20x48@outlook.com',
        url='https://github.com/20x48/RAINLotus',
        version='1.1.0',
        packages=find_packages(),
        package_data={'RAINLotus': ['Template.html', 'Light.css']},
        python_requires='>=3.6',
        project_urls={
            'Github': 'https://github.com/20x48/RAINLotus',
            'Documentation': 'https://docs.20x48.net/RAINLotus'
        },
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
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        ],
        description='✨A new powerful markup language ～ 一门新型的强大的标记语言💪🎄',
        long_description=README.read(),
        long_description_content_type='text/markdown'
    )