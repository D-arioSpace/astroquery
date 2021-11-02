from setuptools import find_packages, setup

setup(
    name = 'ESANEOCC',
    packages = find_packages(include=['ESANEOCC']),
    version = '1.4.0',
    description = 'NEOCC portal Python interface',
    author = 'C. Álvaro Arroyo Parejo',
    license = 'European Space Agency',
    install_requires = ['requests','pandas','parse','scipy','lxml','bs4', 'astropy'],
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest==6.2.1'],
    test_suite = 'test',
)
