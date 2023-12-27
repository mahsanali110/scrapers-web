from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
import date_time
import story
import json
import author
import image
import logging


def get_article_data(current_date):
    base_directory = os.path.dirname(os.path.abspath(__file__))
    project_directory = os.path.join(base_directory)
    date = str(current_date).split('-')
    file_path = project_directory + '/' + 'data' + '/' + date[0] + '/' + date[1] + '/' + date[2] + '/' + "content.json"

    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                categories = json.load(f)

            for category in categories:
                if categories[category]['category_is_scrapped']:
                    articles = categories[category]['articles']  # Get the articles for the current category

                    if articles is not None:  # Check if articles exist
                        for article in articles:
                            try:
                                if not article['article_is_scrapped']:
                                    response = requests.get(article['article_url'])
                                    if response.status_code == 200:
                                        htmlContent = response.content
                                        soup = BeautifulSoup(htmlContent, 'html.parser')
                                        article['article_date'], article['article_time'] = \
                                            date_time.get_datetime(soup)
                                        article['article_story'] = story.get_story(soup)
                                        article['article_author'] = author.get_author(soup)
                                        article['article_is_scrapped'] = True
                                        logging.info('%s - %s - %s - %s', "CATEGORY", category, "ARTICLE IS SCRAPPED",
                                                     article['article_url'])
                                        image_path = image.get_image(soup, current_date)

                                        subfolder_name = 'data'
                                        if image_path is not None:
                                            dirs = image_path.split(os.sep)
                                            subfolder_index = dirs.index(subfolder_name)
                                            shortened_path = os.path.join(*dirs[subfolder_index:])
                                            article['article_image_path'] = shortened_path
                                        else:
                                            article['article_image_path'] = ''

                                        with open(file_path, 'w') as f:
                                            json.dump(categories, f)
                            except Exception as exception:
                                logging.info('%s - %s - %s', "EXCEPTION", category, exception)
                                pass
                    else:
                        logging.info('%s - %s - %s', "CATEGORY", category, "No articles found")
    except FileNotFoundError:
        logging.info('%s - %s', "EXCEPTION", FileNotFoundError)


# Get the current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Call the function with the current date
get_article_data(current_date)
