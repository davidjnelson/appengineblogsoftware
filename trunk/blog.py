"""
Google App Engine Script that handles display of the published
items in the blog.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import os
import sys
import math
import random
import datetime
import urllib

# Google AppEngine imports
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from models import *
import defs
import request
from datetime import tzinfo

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class DateCount(object):
    """
    Convenience class for storing and sorting year/month counts.
    """
    def __init__(self, date, count):
        self.date = date
        self.count = count

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    def __hash__(self):
        return self.date.__hash__()

    def __str__(self):
        return '%s(%d)' % (self.date, self.count)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

class TagCount(object):
    """
    Convenience class for storing and sorting tags and counts.
    """
    def __init__(self, tag, count):
        self.css_class = ""
        self.count = count
        self.url = defs.TAG_URL_PATH + '/' + urllib.quote(tag.replace(' ', '-'))
        self.tag = tag

class AbstractPageHandler(request.BlogRequestHandler):
    """
    Abstract base class for all handlers in this module. Basically,
    this class exists to consolidate common logic.
    """

    def get_tag_counts(self):
        """
        Get tag counts and calculate tag cloud frequencies.
        
        :rtype: list
        :return: list of ``TagCount`` objects, in random order
        """
        tag_counts = Article.get_all_tags()
        result = []
        if tag_counts:
            maximum = max(tag_counts.values())

            for tag, count in tag_counts.items():
                tc = TagCount(tag, count)

                # Determine the popularity of this term as a percentage.

                percent = math.floor((tc.count * 100) / maximum)

                # determine the CSS class for this term based on the percentage

                if percent <= 20:
                    tc.css_class = 'tag-cloud-tiny'
                elif 20 < percent <= 40:
                    tc.css_class = 'tag-cloud-small'
                elif 40 < percent <= 60:
                    tc.css_class = 'tag-cloud-medium'
                elif 60 < percent <= 80:
                    tc.css_class = 'tag-cloud-large'
                else:
                    tc.css_class = 'tag-cloud-huge'
                    
                result.append(tc)

        random.shuffle(result)
        return result

    def get_month_counts(self):
        """
        Get date counts, sorted in reverse chronological order.
        
        :rtype: list
        :return: list of ``DateCount`` objects
        """
        hash = Article.get_all_datetimes()
        datetimes = hash.keys()
        date_count = {}
        for dt in datetimes:
            just_date = datetime.date(dt.year, dt.month, 1)
            try:
                date_count[just_date] += hash[dt]
            except KeyError:
                date_count[just_date] = hash[dt]

        dates = date_count.keys()
        dates.sort()
        dates.reverse()
        return [DateCount(date, date_count[date]) for date in dates]

    def augment_articles(self, articles, url_prefix, html=False):
        """
        Augment the ``Article`` objects in a list with the expanded
        HTML, the path to the article, and the full URL of the article.
        The augmented fields are:
        
        - ``html``: the optionally expanded HTML
        - ``path``: the article's path
        - ``url``: the full URL to the article
        
        :Parameters:
            articles : list
                list of ``Article`` objects to be augmented

            url_prefix : str
                URL prefix to use when constructing full URL from path
                
            html : bool
                ``True`` to generate HTML from each article's RST
        """
        for article in articles:
            article.html = article.body
            article.path = '/' + defs.ARTICLE_URL_PATH + '/%s' % article.id
            article.url = url_prefix + article.path + '/' + urllib.quote(article.title.replace(' ', '-'))
            article.truncated_two_paragraph_html = article.body[0:600]
            if(len(article.body) > 200):
                article.truncated_two_paragraph_html += '...'
            article.published_when = article.published_when.replace(tzinfo=UtcTzinfo()).astimezone(PstTzinfo())

    def render_articles(self,
                        articles,
                        page_title, 
                        request,
                        recent,
                        template_name='show-articles.html'):
        """
        Render a list of articles.
        
        :Parameters:
            articles : list
                list of ``Article`` objects to render

            request : HttpRequest
                the GAE HTTP request object
                
            recent : list
                list of recent ``Article`` objects. May be empty.
                
            template_name : str
                name of template to use
                
        :rtype: str
        :return: the rendered articles
        """
        url_prefix = 'http://' + request.environ['SERVER_NAME']
        port = request.environ['SERVER_PORT']
        if port:
            url_prefix += ':%s' % port

        self.augment_articles(articles, url_prefix)
        self.augment_articles(recent, url_prefix, html=False)

        last_updated = datetime.datetime.now()
        if articles:
            last_updated = articles[0].published_when

        blog_url = url_prefix
        tag_path = '/' + defs.TAG_URL_PATH
        tag_url = url_prefix + tag_path
        date_path = '/' + defs.DATE_URL_PATH
        date_url = url_prefix + date_path
        media_path = '/' + defs.MEDIA_URL_PATH
        media_url = url_prefix + media_path

        template_variables = {'blog_name'    : defs.BLOG_NAME,
        		      'page_title'   : page_title, 
        		      'adsense_publisher_id' : defs.ADSENSE_PUBLISHER_ID, 
        		      'google_custom_search_unique_id' : defs.GOOGLE_CUSTOM_SEARCH_UNIQUE_ID,
                              'blog_owner'   : defs.BLOG_OWNER,
                              'twitter_username' : defs.TWITTER_USERNAME, 
                              'feedburner_account' : defs.FEEDBURNER_ACCOUNT,
                              'full_facebook_fan_page_url' : defs.FULL_FACEBOOK_FAN_PAGE_URL, 
                              'wibiya_javascript_source_link' : defs.WIBIYA_JAVASCRIPT_SOURCE_LINK, 
                              'google_analytics_account_id' : defs.GOOGLE_ANALYTICS_ACCOUNT_ID, 
                              'disqus_username' : defs.DISQUS_USERNAME, 
                              'articles'     : articles,
                              'tag_list'     : self.get_tag_counts(),
                              'date_list'    : self.get_month_counts(),
                              'version'      : '0.3',
                              'last_updated' : last_updated,
                              'blog_path'    : '/',
                              'blog_url'     : blog_url,
                              'archive_path' : '/' + defs.ARCHIVE_URL_PATH,
                              'tag_path'     : tag_path,
                              'tag_url'      : tag_url,
                              'date_path'    : date_path,
                              'date_url'     : date_url,
                              'rss2_path'    : '/' + defs.RSS2_URL_PATH,
                              'recent'       : recent}

        return self.render_template(template_name, template_variables)

    def get_recent(self):
        """
        Get up to ``defs.TOTAL_RECENT`` recent articles.

        :rtype: list
        :return: list of recent ``Article`` objects
        """
        articles = Article.published()

        total_recent = min(len(articles), defs.TOTAL_RECENT)
        if articles:
            recent = articles[0:total_recent]
        else:
            recent = []

        return recent

class UtcTzinfo(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(0)
    def dst(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return 'UTC'
    def olsen_name(self): return 'UTC'
  
class PstTzinfo(datetime.tzinfo):
    """Implementation of the Pacific timezone."""
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-8) + self.dst(dt)

    def _FirstSunday(self, dt):
        """First Sunday on or after dt."""
        return dt + datetime.timedelta(days=(6-dt.weekday()))

    def dst(self, dt):
        # 2 am on the second Sunday in March
        dst_start = self._FirstSunday(datetime.datetime(dt.year, 3, 8, 2))
        # 1 am on the first Sunday in November
        dst_end = self._FirstSunday(datetime.datetime(dt.year, 11, 1, 1))

        if dst_start <= dt.replace(tzinfo=None) < dst_end:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(hours=0)
    def tzname(self, dt):
        if self.dst(dt) == datetime.timedelta(hours=0):
            return "PST"
        else:
            return "PDT"

class FrontPageHandler(AbstractPageHandler):
    """
    Handles requests to display the front (or main) page of the blog.
    """
    def get(self):
        articles = Article.published()
        if len(articles) > defs.MAX_ARTICLES_PER_PAGE:
            articles = articles[:defs.MAX_ARTICLES_PER_PAGE]

        self.response.out.write(self.render_articles(articles, 
        					     'Developer Advocate Blog', 
                                                     self.request,
                                                     self.get_recent()))

class ArticlesByTagHandler(AbstractPageHandler):
    """
    Handles requests to display a set of articles that have a
    particular tag.
    """
    def get(self, tag):
        tag = tag.replace('-', ' ')
        articles = Article.all_for_tag(tag)
        self.response.out.write(self.render_articles(articles,
        					     'Posts with tag: ' + tag, 
                                                     self.request,
                                                     self.get_recent()))

class ArticlesForMonthHandler(AbstractPageHandler):
    """
    Handles requests to display a set of articles that were published
    in a given month.
    """
    def get(self, year, month):
        articles = Article.all_for_month(int(year), int(month))
        self.response.out.write(self.render_articles(articles,
                                                     'Articles for ' + month, 
                                                     self.request,
                                                     self.get_recent()))

class SingleArticleHandler(AbstractPageHandler):
    """
    Handles requests to display a single article, given its unique ID.
    Handles nonexistent IDs.
    """
    def get(self, id):
        article = Article.get(int(id))
        if article:
            template = 'show-articles-single.html'
            articles = [article]
            more = None
        else:
            template = 'not-found.html'
            articles = []

        self.response.out.write(self.render_articles(articles=articles,
                                                     page_title=article.title, 
                                                     request=self.request,
                                                     recent=self.get_recent(),
                                                     template_name=template))

class ArchivePageHandler(AbstractPageHandler):
    """
    Handles requests to display the list of all articles in the blog.
    """
    def get(self):
        articles = Article.published()
        self.response.out.write(self.render_articles(articles,
                                                     'Archived Developer Advocate Blog Posts', 
                                                     self.request,
                                                     [],
                                                     'archive.html'))

class RSSFeedHandler(AbstractPageHandler):
    """
    Handles request for an RSS2 feed of the blog's contents.
    """
    def get(self):
        articles = Article.published()
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(self.render_articles(articles,
                                                     'Developer Advocate RSS Feed', 
                                                     self.request,
                                                     [],
                                                     'rss2.xml'))

class NotFoundPageHandler(AbstractPageHandler):
    """
    Handles pages that aren't found.
    """
    def get(self):
        self.response.out.write(self.render_articles([],
        					     'Not Found', 
                                                     self.request,
                                                     [],
                                                     'not-found.html'))

# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [('/', FrontPageHandler),
     ('/tag/([^/]+)/*$', ArticlesByTagHandler),
     ('/date/(\d\d\d\d)-(\d\d)/?$', ArticlesForMonthHandler),
     ('/id/(\d+).*', SingleArticleHandler),
     ('/archive/?$', ArchivePageHandler),
     ('/rss2/?$', RSSFeedHandler),
     ('/.*$', NotFoundPageHandler),
     ],

    debug=True)

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
