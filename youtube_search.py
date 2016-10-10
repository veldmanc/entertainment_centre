#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import urllib2, urllib, json
import datetime

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyCTQ42Bi09Ol1NXUVK-6ItcyYGYTvfRbhk"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query,max_results):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
      q=query,
      part="id,snippet",
      maxResults=max_results
    ).execute()

    videos = []
    channels = []
    playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":

            searchSplit = search_result["snippet"]["title"].split()

            for subSearch in searchSplit:
                if subSearch not in ignoreFields:
                    lookupInfo = movieInfo(subSearch)
                    if lookupInfo['Response'] == "True":
                        videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                           search_result["id"]["videoId"]))
                        print lookupInfo


    print "Videos:\n", "\n".join(videos), "\n"




if __name__ == "__main__":
    #argparser.add_argument("--q", help="Search term", default="Google")
    #argparser.add_argument("--max-results", help="Max results", default=25)
    #args = argparser.parse_args()

    try:
      youtube_search("2016 Official Movie Trailers", 50)
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
