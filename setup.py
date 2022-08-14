# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'noahs-doves',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = jobpostings.settings']},
)
