
from os import chdir, path
from setuptools import setup
from src import __version__

chdir(path.dirname(path.abspath(__file__)))

with open('readme.md', 'r') as handler:
    readme = handler.read()

setup(
    name='Flask-Plugin',
    version=__version__,
    url='https://github.com/guiqiqi/flask-plugin',
    license='MIT',
    author='Doge Gui',
    author_email='guiqiqi187@gmail.com',
    description='An extension to add support of Plugin in Flask.',
    long_description=readme,
    long_description_content_type="text/markdown",
    zip_safe=False,
    platforms='any',
    python_requires='>=3.7',
    packages=['flask_plugin'],
    package_dir={'flask_plugin': 'src'},
    install_requires=['flask'],
    data_files=[('', ['LICENSE', 'readme.md'])],
    classifiers=[
        'Environment :: Web Environment',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
