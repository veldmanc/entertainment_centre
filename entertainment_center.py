#!/usr/bin/env python

"""Script for curating and viewing a list of movies with movie information and trailers as a web page.

    Creates and maintains a list of movies sorted by popularity within a given year and provides
    functions for opening this list of movie information as a web page

    """

from media import movie
from bs4 import BeautifulSoup
import re
import urllib2, urllib, json
from apiclient.discovery import build
from fresh_tomatoes import open_movies_page
import pickle
import os.path

__author__ = "Chris Veldman"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Chris Veldmsn"
__status__ = "Production"

def fetch_movie_list(result_pages, args):
    """Fetches list of movies.

    Fetches list of movies by scraping results from IMDB. Results are obtained by searching
    for the most popular movies in the year specifed in the arguments

    params:
        result_pages: number of pages from search results to include
        args['imdbPrefix']: url prefix for IMDB query, the string section before the year number
        args['imdbSuffix']: url suffix for IMDB query, the string section after the year number
        args['pageTurnPrefix']: url prefix for IMDB query, the string section before the result page number
        args['pageTurnSuffix']: url prefix for IMDB query, the string section after the result page number
        args['year']: the search parameter that fetches movies within a certain year

    returns:
        A list of candidate movie objects for the final list

    raises:
        none: No exception raising
    """

    movie_list = []

    for pageCount in range(1, result_pages + 1):
        url = args['imdbPrefix'] + str(args['year']) + "," + str(args['year']) + args['imdbSuffix'] + args[
            'pageTurnPrefix'] + str(pageCount) + args['pageTurnSuffix']
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, "lxml")

        links = soup.find_all('a', {'href': re.compile('/title/.*_tt')})
        for link in links:
            movie_list.append(movie(link.text.encode('utf-8'), str(2016).encode('utf-8'), '', '', ''))

    return movie_list


def fetch_movie_info(input_list, args):
    """Fetches info for all movies provided in input_list.

    Fetches info for movies contained in the input_list. Only movies with info available are then
    added to the final output list.

    params:
        input_list: candidate list of movies for inclusion in the list
        args['omdbapi']: url prefix for OMDB api, used to fetch movie info

    returns:
        A list of initialised movie objects, with trailers and movie posters

    raises:
        none: No exception raising
    """

    output_list = []
    assert isinstance(input_list, list)
    for input_movie in input_list:

        # submit query for movie info
        print 'Fetching info for ' + input_movie.title
        query_string = {'t': input_movie.title, 'y': input_movie.year, 'plot': 'full', 'r': 'json'}
        resp = urllib2.urlopen(args['omdbapi'] + urllib.urlencode(query_string))
        movie_info = json.loads(resp.read())

        # if movie info exists then check trailer and poster exists
        if movie_info['Response'] == 'True':
            input_movie.synopsis = movie_info['Plot']
            input_movie.poster_image_url = movie_info['Poster']
            [trailer_found, input_movie.trailer_youtube_url] = youtube_search(input_movie.title, 1, args)

            # If trailer and poster exist then add to filtered output list
            if trailer_found and not input_movie.poster_image_url == 'N/A':
                output_list.append(input_movie)

    return output_list


def youtube_search(query, max_results, args):
    """Fetches youtube video links for the movie with title provided in query

    Fetches trailer url for movie with title in query and containing keywords
    "OFFICIAL" and "TRAILER" in the title.

    params:
        query: the keyword for the youtube search, for example the movie title
        args['YOUTUBE_API_SERVICE_NAME']: name of the google API service we're using
        args['YOUTUBE_API_VERSION']: the version of the API to use
        args['YOUTUBE_DEVELOPER_KEY']: the developer key required to access the API

    returns:
        boolean: Success/Failure
        url: the url for the movie trailer

    raises:
        none: No exception raising
    """

    youtube = build(args["YOUTUBE_API_SERVICE_NAME"], args["YOUTUBE_API_VERSION"],
                    developerKey=args["YOUTUBE_DEVELOPER_KEY"])

    # call the search.list method to retrieve results matching the specified query term.
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results
    ).execute()

    # searcb for official trailer on youtube
    for search_result in search_response.get("items", []):

        resultTitle = search_result["snippet"]["title"].encode('utf-8').upper()
        if ((search_result["id"]["kind"] == "youtube#video") and (query.upper() in resultTitle) and
                ('OFFICIAL' in resultTitle) and ('TRAILER' in resultTitle)):
            return [True, 'https://www.youtube.com/watch?v=' + search_result["id"]["videoId"]]

    return [False, '']


if __name__ == "__main__":

    # read all arguments from config file
    args = json.load(open('config.json'))

    # check if movie list exists otherwise create
    if not os.path.isfile('movies'):
        movies = fetch_movie_info(fetch_movie_list(2, args), args)
        with open('movies', 'wb') as output:
            pickle.dump(movies, output, pickle.HIGHEST_PROTOCOL)
    else:
        with open('movies', 'rb') as input:
            movies = pickle.load(input)

    # Open movies page using fresh tomatoes import
    open_movies_page(movies)
