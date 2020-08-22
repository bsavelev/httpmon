from setuptools import setup

setup(
    name='httpmon',
    version='0.1',
    packages=['tests', 'httpmon'],
    url='https://github.com/bsavelev/httpmon',
    license='BSD',
    author='Boris Savelev',
    author_email='boris.savelev@gmail.com',
    description='Distribution HTTP monitoring tool with Apache Kafka data pipeline and Postgres as storage',
    scripts=('httpmon-cli.py',),
    data_files=[('sql', ['sql/init.sql'])],
    install_requires=[
        'requests',
        'psycopg2',
        'kafka-python',
    ]
)
