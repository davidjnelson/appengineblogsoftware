# $Id: 51015724daff7e7df2558e0f6ff8222dbaa30749 $
#
# Constants used by this application

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# things you'll need to change
# ----------------------------

BLOG_NAME = 'Developer<br/>Advocate'
CANONICAL_BLOG_URL = 'http://developeradvocate.appspot.com/'
BLOG_OWNER = 'David Nelson'
ADSENSE_PUBLISHER_ID = 'pub-1878397330895234'
GOOGLE_CUSTOM_SEARCH_UNIQUE_ID = '014592705538124570741:jjadvz8ftci'
TWITTER_USERNAME = 'devadvocate'
FEEDBURNER_ACCOUNT = 'DeveloperAdvocate'
FULL_FACEBOOK_FAN_PAGE_URL = 'http://www.facebook.com/pages/Developer-Advocate-Blog/245161622572'
WIBIYA_JAVASCRIPT_SOURCE_LINK = 'http://cdn.wibiya.com/Loaders/Loader_27431.js'
GOOGLE_ANALYTICS_ACCOUNT_ID = 'UA-6242674-5'
DISQUS_USERNAME = 'developeradvocateblog'

# things you probably won't need to change
# ----------------------------------------

TEMPLATE_SUBDIR = 'templates'
TAG_URL_PATH = 'tag'
DATE_URL_PATH = 'date'
ARTICLE_URL_PATH = 'id'
MEDIA_URL_PATH = 'static'
ATOM_URL_PATH = 'atom'
RSS2_URL_PATH = 'rss2'
ARCHIVE_URL_PATH = 'archive'
MAX_ARTICLES_PER_PAGE = 5
TOTAL_RECENT = 10

_server_software = os.environ.get('SERVER_SOFTWARE','').lower()
if _server_software.startswith('goog'):
    ON_GAE = True
else:
    ON_GAE = False
del _server_software
