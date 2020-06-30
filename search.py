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

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'AIzaSyBUmOlxftNSGf67nB5DOlBJpj4tImQBU1I'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def getAvailableLanguages(video_id, req_langs=['en','kr']):
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


def download(video_id, languages=[], filetype='srt', root_dir='subtitles/'):
  """Download subtitle of the selected language"""
  
  for i, lang in enumerate(languages):  
    try:
      url = "http://www.youtube.com/api/timedtext?v={0}&lang={1}".format(video_id, lang)
      
      filename = root_dir + video_id + '_' + lang
          
      subtitle = urllib.request.urlopen(url)
            
      if filetype == "srt":
          writeSRTFile(filename, subtitle)
          print('Success :: [https://www.youtube.com/watch?v=%s]' % video_id)
      else:
          writeXMLFile(filename, subtitle)
    
    except Exception:
      # import traceback; print(traceback.format_exc())
      print('Fail ::: ', video_id)
      pass


def writeXMLFile(filename, subtitle):
    with open(filename + ".xml", 'w') as f:
        for line in subtitle:
            f.write(str(line))

def writeSRTFile(filename, subtitle):
    tree = ET.parse(subtitle)
    root = tree.getroot()
    
    with open(filename + ".srt", 'w') as f:
        line = 1
        for child in root:                
            f.write(printSRTLine(line, child.attrib["start"], child.attrib["dur"], child.text.encode('utf-8')))
            line += 1

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



def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

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
      vidoeId = search_result['id']['videoId']

      # Check Subtitle existance
      langs = getAvailableLanguages(vidoeId)
      
      if 'kr' in langs or 'en' in langs:
        # print(langs)
        download(vidoeId, langs, 'srt')

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
  parser.add_argument('--q', help='Search term', default='Google')
  parser.add_argument('--max-results', help='Max results', default=1000)
  args = parser.parse_args()

  try:
    youtube_search(args)
  except HttpError as e:
    print ('An HTTP error %d occurred:\n%s' % e.resp.status, e.content)
