try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Semantic Selector',
    'author': 'Toshiya Komoda',
    'url': 'https://github.com/toshiya/semantic_selector',
    'download_url': 'https://github.com/toshiya/semantic_selector',
    'author_email': 'toshiya.komoda@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'install_requires': [
        "mysql-connector",
        "gensim",
        "beautifulsoup4",
        "mecab-python3",
        "sklearn",
    ],
    'packages': ['semantic_selector'],
    'name': 'semantic_selector'
}
