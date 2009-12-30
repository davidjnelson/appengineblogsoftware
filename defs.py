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

BLOG_NAME = 'Blog Name'
CANONICAL_BLOG_URL = 'http://yoururl.com/'
BLOG_OWNER = 'Your Name'
ADSENSE_PUBLISHER_ID = 'pub-12345'
GOOGLE_CUSTOM_SEARCH_UNIQUE_ID = '12345:iiiii'
TWITTER_USERNAME = 'yourtwitterusername'
FEEDBURNER_ACCOUNT = 'yourfeedburneraccount'
FULL_FACEBOOK_FAN_PAGE_URL = 'http://www.facebook.com/pages/YOURFACEBOOKFANPAGEEXTRAURLINFO'
WIBIYA_JAVASCRIPT_SOURCE_LINK = 'http://cdn.wibiya.com/Loaders/YOURCUSTOMURL.js'
GOOGLE_ANALYTICS_ACCOUNT_ID = 'UA-12345'
DISQUS_USERNAME = 'yourdisqususername'

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
