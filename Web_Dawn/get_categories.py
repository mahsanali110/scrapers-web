import logging
import os
import requests
import json
from dateutil import parser
from datetime import datetime


def get_categories(categories, current_date):
    try:
        for category in categories:

            base_directory = os.path.dirname(os.path.abspath(__file__))
            project_directory = os.path.join(base_directory)
            url = categories[category]['category_url'] + current_date
            date = current_date.split('-')
            file_path = project_directory + '/' + 'data' + '/' + date[0] + '/' + date[1] + '/' + date[
                2] + '/' + "content.json"

            response = requests.get(url)
            if response.status_code == 200:
                htmlContent = response.content
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(htmlContent, 'html.parser')

                data = soup.find_all('article', class_="mb-4")

                processed_urls = set()  # Set to store processed article URLs

                for article in data:
                    article_dict = dict(newspaper='The Dawn',
                                        article_url='',
                                        article_date='',
                                        article_time='',
                                        article_headline='',
                                        article_story='',
                                        article_author='',
                                        article_is_scrapped=False,
                                        batch=False
                                        )

                    article_dict['newspaper'] = 'The Dawn'
                    article_dict['article_headline'] = article.find('a', {"class": "story__link"}).text.strip()

                    if category == 'Web Archive':
                        article_dict['article_url'] = article.find('a', {"class": "story__link"})['href']
                    else:
                        article_dict['article_url'] = article.find("a")['href']

                    if article_dict['article_url'] in processed_urls:

                        continue  # Skip the article if its URL has already been processed

                    processed_urls.add(article_dict['article_url'])  # Add the URL to the processed set

                    duplicate_found = False

                    for cat in categories:
                        existing_urls = [article['article_url'] for article in categories[cat]['articles']]
                        if article_dict['article_url'] in existing_urls:
                            duplicate_found = True
                            break

                    if duplicate_found:
                        continue  # Skip the article if it already exists in any category

                    # Check if the category is mentioned in the list of specific categories
                    if category in ['Editorial', 'Column', 'National Days', 'Lifestyle', 'Education',
                                    'Agriculture', 'Yearender', 'Other Voices', '50 Years Ago Today',
                                    'Letters to the Editor']:
                        article_date_str = article.find('span', class_="timestamp--time")['title']
                        article_date = parser.isoparse(article_date_str).date()
                        if article_date == datetime.strptime(current_date, "%Y-%m-%d").date():
                            categories[category]['articles'].append(article_dict)
                    else:
                        categories[category]['articles'].append(article_dict)

                categories[category]['category_is_scrapped'] = True

                # write some data to the file
                with open(file_path, 'w') as f:
                    json.dump(categories, f)

        return True
    except Exception as exception:
        logging.info('%s - %s', "EXCEPTION", exception)
