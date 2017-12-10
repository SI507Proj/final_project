import json
import datetime
import logging
import sys

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
CACHE_FNAME = 'cache_file.json'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
EXPIRE_IN_MIN = 30

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class CacheManager(object):
    def __init__(self):
        # Load cache file
        try:
            with open(CACHE_FNAME, 'r') as cache_file:
                cache_json = cache_file.read()
                self.cache_diction = json.loads(cache_json)
        except:
            self.cache_diction = {}

    def clear_cache(self):
        self.cache_diction.clear()

    def has_cache_expired(self, timestamp_str):
        """Check if cache timestamp is over expire_in_min old"""
        # gives current datetime
        now = datetime.datetime.now()

        # datetime.strptime converts a formatted string into datetime object
        cache_timestamp = datetime.datetime.strptime(timestamp_str, DATETIME_FORMAT)

        # subtracting two datetime objects gives you a timedelta object
        delta = now - cache_timestamp
        delta_in_min = round(delta.total_seconds() / 60)

        # now that we have days as integers, we can just use comparison
        # and decide if cache has expired or not
        if delta_in_min <= EXPIRE_IN_MIN:
            return False
        else:
            logging.debug("Cache Time Expired")
            return True

    def get_from_cache(self, unique_ident):
        """If URL exists in cache and has not expired, return the html, else return None"""
        if unique_ident in self.cache_diction:
            unique_ident_dict = self.cache_diction[unique_ident]

            if self.has_cache_expired(unique_ident_dict['timestamp']):
                # also remove old copy from cache
                del self.cache_diction[unique_ident]
                resp = None
            else:
                resp = self.cache_diction[unique_ident]['resp']
        else:
            resp = None
        return resp

    def set_in_cache(self, unique_ident, resp):
        """Add response to the cache dictionary, and save the whole dictionary to a file as json"""
        self.cache_diction[unique_ident] = {
            'resp': resp,
            'timestamp': datetime.datetime.now().strftime(DATETIME_FORMAT),
        }

        with open(CACHE_FNAME, 'w') as cache_file:
            cache_json = json.dumps(self.cache_diction)
            cache_file.write(cache_json)
