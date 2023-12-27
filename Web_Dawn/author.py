import logging


def get_author(soup):
    try:
        span_text = soup.find('span', {"class": "story__byline"})
        author = span_text.text.strip()
        return author
    except Exception as excep:
        logging.info('%s - %s', "EXCEPTION IN GET AUTHOR FUNCTION", excep)
