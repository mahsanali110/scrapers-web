import logging


def get_title(soup):
    try:
        title = soup.find('a', {"class": "story__link"}).text
        return title
    except Exception as excep:
        logging.info('%s - %s', "EXCEPTION IN GET TITLE FUNCTION", excep)
