from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, RuntimeError):
    long_description = ''

setup(
    name='django-computedfields',
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    version='0.0.2',
    license='MIT',
    description='autogenerated and autoupdated database fields for decorated model methods',
    long_description=long_description,
    author='netzkolchose',
    author_email='j.breitbart@netzkolchose.de',
    url='https://github.com/netzkolchose/django-computedfields',
    download_url='https://github.com/netzkolchose/django-computedfields/archive/0.0.2.tar.gz',
    keywords=['django', 'method', 'decorator', 'autoupdate', 'persistent'],
    classifiers=[],
)