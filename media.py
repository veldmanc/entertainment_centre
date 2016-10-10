
# movie class
class movie:

    # class constructor
    def __init__(self, title, year, synopsis='', poster_image_url='', trailer_youtube_url=''):

        # movie title
        self.title = title

        # year of release
        self.year = year

        # synopsis
        self.synopsis = synopsis

        # url for box art
        self.poster_image_url = poster_image_url

        # url for youtube trailer
        self.trailer_youtube_url = trailer_youtube_url

