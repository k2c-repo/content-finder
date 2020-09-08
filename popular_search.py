import argparse
import urllib.request
from urllib.parse import urlparse, parse_qs, parse_qsl
import argparse
import sys
import xml.etree.ElementTree as ET
import json

DEVELOPER_KEY = 'AIzaSyBUmOlxftNSGf67nB5DOlBJpj4tImQBU1I'


def search_popular(options):
    url = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet\
&chart=mostPopular&regionCode=%s&videoCategoryId=%s&maxResults=%s&key=%s"\
%(options.region_code, options.video_category, options.max_results, DEVELOPER_KEY)

    # print(url)

    response = urllib.request.urlopen(url)
    item_list = json.loads(response.read()).get('items', [])

    rtn_list = []

    for _, v in enumerate(item_list):
        print('%s \n[https://www.youtube.com/watch?v=%s]\n' % (v['snippet']['title'], v['id']))
        rtn_list.append(v['id'])

    return rtn_list


if __name__ == '__main__':
  parser = argparse.ArgumentParser()  
  parser.add_argument('--region_code', '-r', help='Region Code', default='kr')
  parser.add_argument('--video_category', '-v', help='Video Category', default=0)
  parser.add_argument('--max_results', '-m', help='Max results', default=50)
  
  args = parser.parse_args()

  try:    
    rtn = search_popular(args)
    # print(rtn)
  except Exception as e:
    print(e)
    # print ('An HTTP error %d occurred:\n%s' % e.resp.status, e.content)

# https://www.googleapis.com/youtube/v3/videos?part=id,%20snippet,statistics,contentDetails&videoCategoryId=1
# &chart=mostPopular&regionCode=kr&maxResults=25&key=AIzaSyBUmOlxftNSGf67nB5DOlBJpj4tImQBU1I