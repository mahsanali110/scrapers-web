import logging
from datetime import datetime


def get_datetime(soup):
    try:
        date_string = soup.find('span', {"class": "timestamp--time"})
        if date_string is None:
            date_string = soup.find('span', {"class": "story__time text-center text-3.5 leading-none text-gray-500 tracking-wider"})
            if date_string is None:
                date_string = soup.find('span', {"class": "timestamp--date"})  # Add this line
                if date_string is None:
                    # Handle the case when no date is found
                    return None, None
                date_string = date_string.text.strip()

                # Extract the date from the string
                datetime_obj = datetime.strptime(date_string, '%B %d, %Y')
                article_date = datetime_obj.strftime('%d/%m/%Y')
                article_time = datetime.now().strftime('%I:%M %p')
            else:
                date_string = date_string.text.strip()
                if not date_string:
                    # Handle the case when the date string is empty
                    return None, None
                # Extract the date from the string
                if date_string.startswith('Updated'):
                    date_string = date_string[7:].strip()

                datetime_obj = datetime.strptime(date_string, '%d %b, %Y')
                article_date = datetime_obj.strftime('%d/%m/%Y')
                article_time = datetime.now().strftime('%I:%M %p')
        else:
            date_string = date_string.get('title')
            if date_string is None:
                # Handle the case when no date is found
                return None, None
            datetime_obj = datetime.fromisoformat(date_string)
            article_date = datetime_obj.strftime('%d/%m/%Y')
            article_time = datetime_obj.strftime('%I:%M %p')

        return article_date, article_time
    except Exception as excep:
        logging.info('%s - %s', "EXCEPTION IN GET_DATE_TIME FUNCTION", excep)
