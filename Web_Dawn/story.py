import logging


def get_story(soup):
    try:
        data = soup.find('div', class_="story__content").text.replace("\n", "")
        return data
    except Exception as excep:
        logging.info('%s - %s', "EXCEPTION IN GET STORY FUNCTION", excep)
