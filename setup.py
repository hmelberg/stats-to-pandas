from distutils.core import setup
setup(
  name = 'stats-to-pandas',
  packages = ['stats-to-pandas'], # this must be the same as the name above
  version = '0.0.1',
  description = 'Import data from Statistics Norway, Sweden, Ireland and the UK to a Pandas dataframe in Python',
  author = 'Hans Olav Melberg',
  author_email = 'hans.melberg@gmail.com',
  url = 'https://github.com/hmelberg/stats-to-pandas', # use the URL to the github repo
  download_url = 'https://github.com/hmelberg/stats-to-pandas/tarball/0.0.1', # I'll explain this in a second
  keywords = ['pandas', 'Statistics Norway', 'json-stat'], # arbitrary keywords
  classifiers = [],
)