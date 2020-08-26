#!/usr/bin/python

# This sample executes a search request for the specified search term.
# Sample usage:
#   python search.py --q=surfing --max-results=10
# NOTE: To use the sample, you must provide a developer key obtained
#       in the Google APIs Console. Search for "REPLACE_ME" in this code
#       to find the correct place to provide that key..

import argparse
import urllib.request
from urllib.parse import urlparse, parse_qs, parse_qsl
import argparse
import sys
import xml.etree.ElementTree as ET
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database import database

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'AIzaSyBUmOlxftNSGf67nB5DOlBJpj4tImQBU1I'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Firebase DB init
db = database('key.json')

def getAvailableLanguages(video_id, req_langs=['en','ko']):
    """Get all available languages of subtitle"""
    try:
      url = "http://www.youtube.com/api/timedtext?v=%s&type=list" % video_id
      xml = urllib.request.urlopen(url)
      tree = ET.parse(xml)
      root = tree.getroot()
      # languages = {}
      languages = []

      for child in root:
          if child.attrib['lang_code'] in req_langs:
          # languages[child.attrib["lang_code"]] = child.attrib["lang_translated"]
            languages.append(child.attrib['lang_code'])
    
    except Exception:
      import traceback; print(traceback.format_exc())
      pass
    
    return languages


def download(video_id, video_title, languages, search_key, filetype='srt', root_dir='subtitles/'):
  """Download subtitle of the selected language"""

  subtitles = {}
  check = True

  for _, lang in enumerate(languages):  
    try:
      url = "http://www.youtube.com/api/timedtext?v={0}&lang={1}".format(video_id, lang)      
      filename = root_dir + video_id + '_' + lang
      subtitle = urllib.request.urlopen(url)
      
      if filetype == "srt":
          subtitles[lang] = writeSRTFile(filename, subtitle)
      else:
          writeXMLFile(filename, subtitle)

      print('Download Success[%s] :: [https://www.youtube.com/watch?v=%s] %s' % (lang, video_id, video_title))
    
    except Exception as ex:
      # import traceback; print(traceback.format_exc())
      print('Fail(Video ID) ::: ', video_id, ex)
      # pass
      check = False
      continue

  # Insert to Firebase Cloud Firestore
  if check:
    try:
      data = {'title': video_title,
              'link': 'https://www.youtube.com/watch?v='+video_id,
              'subtitles': subtitles,
              'keyword': search_key}

      db.write('contents', video_id, **data)

      print('Firebase DB Insert Completed!!')
    except Exception as ex:
      print(ex)


def writeXMLFile(filename, subtitle):
    with open(filename + ".xml", 'w') as f:
        for line in subtitle:
            f.write(str(line))


def writeSRTFile(filename, subtitle):
    tree = ET.parse(subtitle)
    root = tree.getroot()
    str_list = []
    
    with open(filename + ".srt", 'w') as f:
        line = 1
        for child in root:                
            text = printSRTLine(line, child.attrib["start"], child.attrib["dur"], child.text.encode('utf-8'))
            f.write(text)
            line += 1
            str_list.append(text)            
        
        return ''.join(str_list)


def formatSRTTime(secTime):
    """Convert a time in seconds (in Google's subtitle) to SRT time format"""
    sec, micro = str(secTime).split('.')
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return "{:02}:{:02}:{:02},{}".format(h,m,s,micro)


def printSRTLine(line, start, duration, text):        
    """Print a subtitle in SRT format"""
    end = formatSRTTime(float(start) + float(duration))
    start = formatSRTTime(float(start))
    # end = float(start) + float(duration)
    text = convertHTML(text.decode('utf-8'))
    return "{}\n{} --> {}\n{}\n\n".format(line, start, end, text)


def convertHTML(text):
    return text.replace('&#39;', "'")


def checkEmbeddable(videoId):
  url = "https://www.googleapis.com/youtube/v3/videos?id=%s&part=status&key=%s" % (videoId, DEVELOPER_KEY)
  response = urllib.request.urlopen(url)
  
  # data structure(json) : items -> status -> embeddable 
  embeddable = json.loads(response.read()).get('items', [])[0]['status']['embeddable']
  return embeddable


def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    part='id,snippet',
    maxResults=options.max_results
  ).execute()

  videos = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videoeId = search_result['id']['videoId']
      videoTitle = convertHTML(search_result['snippet']['title'])
      # print('vidoeId ::: ', vidoeId)

      # print(checkEmbeddable(videoeId))
      # Enable Check for iFrame Play
      if not checkEmbeddable(videoeId):
        continue

      # Check Subtitle existance
      langs = getAvailableLanguages(videoeId)
      # print('langs :::: ', langs)
      
      if 'ko' in langs and 'en' in langs:
        # print(langs)
        download(videoeId, videoTitle, langs, options.q, 'srt')

      # videos.append('%s\n[https://www.youtube.com/watch?v=%s]\n' % (search_result['snippet']['title'],
      #                            search_result['id']['videoId']))
    # elif search_result['id']['kind'] == 'youtube#channel':
    #   channels.append('%s (%s)' % (search_result['snippet']['title'],
    #                                search_result['id']['channelId']))
    # elif search_result['id']['kind'] == 'youtube#playlist':
    #   playlists.append('%s (%s)' % (search_result['snippet']['title'],
    #                                 search_result['id']['playlistId']))

  # print ('Videos:\n', '\n'.join(videos), '\n')
  # print ('Channels:\n', '\n'.join(channels), '\n')
  # print ('Playlists:\n', '\n'.join(playlists), '\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--q', '-q', help='Search term', default='Google')
  parser.add_argument('--max_results', '-m', help='Max results', default=1000)
  args = parser.parse_args()

  try:
    # Process Flow
    # youtube_search -> checkEmbeddable -> getAvailableLanguages -> download
    youtube_search(args)
  except HttpError as e:
    print ('An HTTP error %d occurred:\n%s' % e.resp.status, e.content)