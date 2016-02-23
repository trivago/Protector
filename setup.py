from setuptools import setup, find_packages

# Pull version from source without importing
# since we can't import something we haven't built yet :)
exec (open('protector/version.py').read())

# Create reStructuredText README file for PyPi
# http://stackoverflow.com/a/26737672/270334
try:
    import pypandoc

    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

requires = [
    "daemonocle",
    "dateparser",
    "funcsigs",
    "httpretty",
    "jdatetime",
    "pbr",
    "python-dateutil",
    "PyYAML",
    "result",
    "wheel"
]

test_requires = [
    "coverage",
    "freezegun",
    "mock",
    'nose',
    'nose-cover3',
    "six"
]

setup(name='protector',
      version=__version__,
      description='A circuit breaker for Time series databases like InfluxDB that prevents expensive queries',
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Topic :: Utilities',
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: Implementation :: PyPy",
      ],
      keywords='influxdb proxy graphite circuit-breaker',
      url='http://github.com/trivago/protector',
      author='Matthias Endler',
      author_email='matthias.endler@trivago.com',
      license='BSD',
      packages=find_packages(),
      install_requires=requires,
      test_suite='nose.collector',
      tests_require=test_requires,
      entry_points={
          'console_scripts': ['protector=protector.__main__:main'],
      },
      include_package_data=True,
      zip_safe=False)
