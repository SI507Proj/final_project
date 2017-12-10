# https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps
# https://developers.google.com/youtube/v3/docs/search/list

import os
import sys
import logging
import datetime

import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from youtube_manager import *
from cache_manager import *

#gae_dir = google.__path__.append('/path/to/appengine_sdk//google_appengine/google')
#sys.path.insert(0, gae_dir) # might not be necessary
#import google.appengine # now it's on your import path`

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret_web.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#@app.route('/')
#def index():
#  return print_index_table()

@app.route('/')
def youtube_api_request():
  if 'credentials' not in flask.session:
    logging.debug("authorize credentials")
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  region_trends = query_region_trend(client)
  info_to_embed = []
  for trend in region_trends:
      info_to_embed.append(trend.get_info_to_embed())

  return flask.render_template('youtube.html', items_to_embed=info_to_embed)

@app.route('/region_db')
def show_db():
    region = flask.request.args.get('q')
    response = trend_manager.query_by_region(region)

    items = []
    for info in response:
        items.append("%s (%s)" % (info['Title'], info['ID']))

    return flask.render_template('region_db.html', items=items)


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('youtube_api_request'))

@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

def query_region_trend(client):
    region_trends = []
    quries = trend_manager.reg_quries # codes = ['US', 'KR']

    for query in quries:
        videos = video_list_by_popular(client, query)
        video_objs = []
        for item in videos:
            video = Video(item)
            video_objs.append(video)

        region_code = query['region_code']
        region_info = {CODE: region_code, REGION: trend_manager.code_to_name[region_code]}
        region_trend = RegionTrend(region_info, video_objs)
        trend_manager.insert_to_db(region_trend)
        region_trends.append(region_trend)

    return region_trends

def params_unique_combination(baseurl, options):
    alphabetized_keys = sorted(options.keys())
    res = []
    for k in alphabetized_keys:
            res.append("{}-{}".format(k, options[k]))
    return baseurl + "_".join(res)

def video_list_by_popular(client, options):
  # check if the response is already in cache
  unique_ident = params_unique_combination('https://www.googleapis.com/youtube/v3/videos', options)
  response = cache_manager.get_from_cache(unique_ident)

  # request video list if not in cache and save it to cache!
  if response == None:
      logging.debug("not in cache, request url")
      response = client.videos().list(
          part='snippet,contentDetails,statistics',
          chart='mostPopular',
          maxResults=options['max_results'],
          regionCode=options['region_code']
      ).execute()
      cache_manager.set_in_cache(unique_ident, response)

  # parse video id, title, kind from the response and save it to list
  logging.debug("video_response: {}".format(response))
  videos = []
  for video_result in response.get('items', []):
    if video_result[KIND] == 'youtube#video':
        video = {}
        video[KIND] = 'video'
        video[TITLE] = video_result['snippet']['title']
        video[ID] = video_result['id']
        videos.append(video)

  return videos

def search_list_by_location(client, options):
  search_response = client.search().list(
    type='video',
    location=options['location'],
    locationRadius=options['location_radius'],
    part='id,snippet',
    maxResults=options['max_results'],
    order=options['order'],
    publishedAfter=options['publishedAfter']
  ).execute()

  videos = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  logging.debug("search_response type: {}".format(search_response))

  for search_result in search_response.get('items', []):
    # logging.debug("search_response {}".format(search_result))
    if search_result['id']['kind'] == 'youtube#video':
      videos.append('%s (%s)' % (search_result['snippet']['title'],
                                 search_result['id']['videoId']))
    elif search_result['id']['kind'] == 'youtube#channel':
      channels.append('%s (%s)' % (search_result['snippet']['title'],
                                   search_result['id']['channelId']))
    elif search_result['id']['kind'] == 'youtube#playlist':
      playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                    search_result['id']['playlistId']))
  return videos

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  cache_manager = CacheManager()
  trend_manager = TrendManager()

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)
