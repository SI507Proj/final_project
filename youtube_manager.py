import sys
import logging

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Video info
REGION = 'region'
KIND = 'kind'
TITLE = 'title'
ID = 'id'
URL = 'url'

# Region info
CODE = 'code'
REGION = 'region'
URLS = 'urls'

class TrendManager(object):
    codes = ['US', 'KR']
    code_to_name = {'US': 'USA', 'KR': 'Korea'}
    def __init__(self):
        self.loc_quries = self.__generate_location_query()
        self.reg_quries = self.__generate_region_query()

    def __generate_location_query(self):
        quries = []
        options = {}
        options['location'] = '42.280826,-83.743038'
        options['location_radius'] = '30mi'
        options['max_results'] = 10
        options['order'] = 'rating'
        options['publishedAfter'] = '2017-01-01T00:00:00.0Z'
        return quries

    def __generate_region_query(self):
        quries = []
        for code in self.codes:
            options = {}
            options['max_results'] = 10
            options['region_code'] = code
            quries.append(options)
        return quries

class Video(object):
    def __init__(self, item):
        self.kind  = item[KIND]
        self.title = item[TITLE]
        self.id    = item[ID]
        self.url   = "http://www.youtube.com/embed/{0}".format(item[ID])

    def __str__(self):
        return "%s (%s)" % (self.title, self.id)

    def __repr__(self):
        return "%s" % self.id

    def __contains__(self, word):
        return word in self.title

class RegionTrend(object):
    def __init__(self, region_info, video_list):
        self.code = region_info[CODE]
        self.region = region_info[REGION]
        self.videos = video_list

    def get_info_to_embed(self):
        url_list = []
        for video in self.videos:
            url_list.append(video.url)
        embedded_info = {REGION: self.region, URLS: url_list}
        return embedded_info

    def __repr__(self):
        return "%s" % self.region
