import requests
import logging
import os
import re
import json
from ssl import SSLError
from bs4 import BeautifulSoup
from log_file import create_log
import month_day_mapping_dict


def run_pakistan_today():
    create_log()

    logging.info('%s', "SCRAPPING STARTED OF PAKISTAN TODAY")
    url = "https://www.pakistantoday.com.pk/category/opinion-pt/"

    # Send a GET request to the URL
    response = requests.get(url)

    article_data_dict = {}

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with class "vc_column-inner"
    div_element = soup.find('div', class_="td-ss-main-content")

    # Find all 'h3' elements with class "entry-title td-module-title" within the div
    h3_elements = div_element.find_all('h3', class_='entry-title td-module-title')

    # Extract and print the href attribute from the 'a' tags
    for h3 in h3_elements:
        try:
            link = h3.find('a')
            article_url = link.get('href')
            response = requests.get(article_url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
            })
            if response.status_code == 200:
                logging.info('%s - %s', "Print status code: ", response.status_code)
                article_soup = BeautifulSoup(response.content, 'html.parser')

                p_tags1 = article_soup.find('div', class_='td_block_wrap tdb_single_content tdi_45 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')
                p_tags = p_tags1.find_all('p')
                if p_tags:
                    article_story = ''
                    for item in p_tags:
                        article_story += item.text
                else:
                    logging.info('%s - %s', "p has no text: ", article_url)

                # Get the title
                article_title = article_soup.find('h1', class_='tdb-title-text')
                if article_title:
                    title_h1 = article_title.text
                else:
                    logging.info('%s - %s', "No title: ", article_url)

                # Get the author name
                article_by_author = article_soup.find('a', class_='tdb-author-name')
                if article_by_author:
                    article_author = article_by_author.text

                # Get publish date
                article_publish_date = article_soup.find('time', class_='entry-date updated td-module-date')
                if article_publish_date:
                    article_publish_date_text = article_publish_date.text
                    words = article_publish_date_text.strip().split()   # SPLIT THE TEXT INTO INDIVIDUAL WORDS

                    word_indices = {}
                    for index, word in enumerate(words):
                        word_indices[index] = word

                    publish_date = word_indices[2] + '-' + month_day_mapping_dict.month_day_mapping[word_indices[0]] + '-' + month_day_mapping_dict.month_day_mapping[word_indices[1]]
                else:
                    publish_date = ''

                current_time = datetime.datetime.now().time()
                formatted_time = current_time.strftime("%I:%M %p")

                # Get the image from link
                image_tag = article_soup.find('div', 'td_block_wrap tdb_single_featured_image tdi_44 tdb-content-horiz-left td-pb-border-top td_block_template_1').find('img')
                if image_tag:
                    image_link = image_tag['src']
                    image_data = requests.get(image_link).content
                    image_name = os.path.basename(image_link)
                    image_folder = os.path.join(os.getcwd() , "data", publish_date.replace('-', '/') , "Pakistan Today", "images")
                    os.makedirs(image_folder, exist_ok=True)
                    image_name_title = re.sub(r'[<>:"/\\|?*]', '', title_h1)
                    image_path = os.path.join(image_folder, f'{image_name_title}.jpg')
                    if os.path.exists(image_path):
                        logging.info('%s - %s', "Image already exists: ", article_title)
                    else:
                        try:
                            with open(image_path, 'wb') as f:
                                f.write(image_data)
                            logging.info('%s - %s', "Image downloaded: ", article_title)
                        except:
                            logging.info('%s - %s', "Error: Failed to download image: ", article_title)
                        # Get the relative path from the base directory
                    image_path_short = '/'.join(image_path.split(os.sep)[5:])  # convert os.sep to '/'
                else:
                    image_path_short = None

                # Create a dictionary with the article data
                article_data = {
                    'Article_Headline': title_h1,
                    'Article_Story': article_story,
                    'Article_Author': article_author,
                    'Article_Publish_date': publish_date,
                    'Atricle_Publish_time': formatted_time,
                    'Article_url': article_url,
                    'Article_Scraped': True,
                    'Batch': False,
                    'article_image_url': image_path_short
                }
                # Append the article data to the dictionary for this date
                if publish_date not in article_data_dict:
                    article_data_dict[publish_date] = {
                        'Channel Name': 'Pakistan Today',
                        'Webite_url': url,
                        'Articles': []
                    }
                article_data_dict[publish_date]['Articles'].append(article_data)

                # Save the JSON file if the article is present
                if title_h1:
                    folder_path = os.path.join(os.getcwd(), 'data', publish_date.replace('-', os.sep),
                                               'Pakistan Today')
                    # Create the directory if the article is present
                    os.makedirs(folder_path, exist_ok=True)

                    # Check if the JSON file already exists
                    json_file_path = os.path.join(folder_path, 'content.json')
                    if os.path.exists(json_file_path):
                        # If the JSON file exists, read its contents and check if the article is already published
                        with open(json_file_path, 'r') as json_file:
                            existing_data = json.load(json_file)
                            articles = existing_data['Articles']

                            # Check if the article is already present based on the URL
                            article_present = any(article['Article_url'] == article_url for article in articles)

                            if article_present:
                                logging.info('%s - %s', "Article already published: ", publish_date)
                            else:
                                # Append the new article to the existing data
                                articles.append(article_data)

                                # Save the updated JSON file
                                with open(json_file_path, 'w') as outfile:
                                    json.dump(existing_data, outfile)

                                logging.info('%s - %s', "New article appended to existing JSON file: ", json_file_path)

                    else:
                        # If the JSON file doesn't exist, create a new dictionary and add the article data
                        article_data_dict[publish_date] = {
                            'Channel Name': 'Pakistan Today',
                            'Webite_url': url,
                            'Articles': [article_data]
                        }

                        # Save the JSON file
                        with open(json_file_path, 'w') as outfile:
                            json.dump(article_data_dict[publish_date], outfile)

                        logging.info('%s - %s', "New JSON file created for the date: ", publish_date)
        except (ConnectionError, SSLError) as e:
            logging.error('%s - %s', "Error occurred while making the request:", str(e))
            continue

        except requests.exceptions.RequestException as e:
            logging.error('%s - %s', "Error occurred during the request:", str(e))
            continue

        except Exception as e:
            logging.error('%s - %s', "An unexpected error occurred:", str(e))
            continue
