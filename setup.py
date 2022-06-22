
# -*- coding: utf-8 -*-
from setuptools import setup

long_description = None
# Read requirements.txt, ignore comments
try:
    INSTALL_REQUIRES = list()
    f = open("requirements.txt", "rb")
    for line in f.read().decode("utf-8").split("\n"):
        line = line.strip()
        if "#" in line:
            line = line[: line.find("#")].strip()
        if line:
            INSTALL_REQUIRES.append(line)
except FileNotFoundError:
    print("'requirements.txt' not found!")
    INSTALL_REQUIRES = list()



setup_kwargs = {
    'name': '',
    'version': '',
    'description': '',
    'long_description': long_description,
    'license': 'MIT',
    'author': '',
    'author_email': 'dev <dev@gmail.com>',
    'maintainer': None,
    'maintainer_email': None,
    'url': '',
    'packages': [
        'finrl',
        'unit_testing',
        'old.finrl',
        'old.finrl.applications',
        'old.finrl.finrl_meta',
        'old.finrl.agents',
        'old.finrl.applications.cryptocurrency_trading',
        'old.finrl.applications.portfolio_allocation',
        'old.finrl.applications.stock_trading',
        'old.finrl.applications.high_frequency_trading',
        'old.finrl.finrl_meta.data_processors',
        'old.finrl.finrl_meta.preprocessor',
        'old.finrl.finrl_meta.env_cryptocurrency_trading',
        'old.finrl.finrl_meta.env_portfolio_allocation',
        'old.finrl.finrl_meta.env_stock_trading',
        'old.finrl.agents.stablebaselines3',
        'old.finrl.agents.rllib',
        'old.finrl.agents.elegantrl',
        'finrl.applications',
        'finrl.finrl_meta',
        'finrl.agents',
        'finrl.applications.cryptocurrency_trading',
        'finrl.applications.portfolio_allocation',
        'finrl.applications.stock_trading',
        'finrl.applications.high_frequency_trading',
        'finrl.finrl_meta.data_processors',
        'finrl.finrl_meta.preprocessor',
        'finrl.finrl_meta.env_cryptocurrency_trading',
        'finrl.finrl_meta.env_portfolio_allocation',
        'finrl.finrl_meta.env_stock_trading',
        'finrl.agents.stablebaselines3',
        'finrl.agents.rllib',
        'finrl.agents.elegantrl',
        'unit_testing.test_env',
        'unit_testing.test_marketdata',
        'unit_testing.test_alpaca',
    ],
    'package_data': {'': ['*']},
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '==3.9.9',

}


setup(**setup_kwargs)
