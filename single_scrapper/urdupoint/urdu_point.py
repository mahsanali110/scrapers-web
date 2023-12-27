from ssl import SSLError
from bs4 import BeautifulSoup
import os
import logging
import json
import requests
import re
import datetime

base_directory = os.path.dirname(os.path.abspath(__file__))
project_directory = os.path.join(base_directory)

def create_log():
    try:
        x = datetime.datetime.now()
        year = x.strftime("%Y")
        month = x.strftime("%B")
        day = x.strftime("%x")
        log_day = day.split("/")
        log_path = project_directory + "/" + "log"
        log_file = os.path.isdir(log_path)
        year_path = project_directory + "/" + "log" + "/" + str(year)
        year_file = os.path.isdir(year_path)
        month_path = project_directory + "/" + "log" + "/" + str(year) + "/" + str(month)
        month_file = os.path.isdir(month_path)
        day_folder_path = project_directory + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(log_day[1])
        day_folder_file = os.path.isdir(day_folder_path)
        day_path = project_directory + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(log_day[1]) \
                   + "/urdupoint_urdunews.log"
        if not log_file:
            os.mkdir(log_path)
        if not year_file:
            os.mkdir(year_path)
        if not month_file:
            os.mkdir(month_path)
        if not day_folder_file:
            os.mkdir(day_folder_path)
        logging.basicConfig(filename=day_path, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.INFO, force=True)
        return logging
    except Exception as exception:
        logging.info('%s - %s', "LOG DID NOT CREATE", exception)

def run_urdu_news():
    create_log()
    month_day_mapping = {
        'جنوری': '01',
        'فروری': '02',
        'مارچ': '03',
        'اپریل': '04',
        'مئی': '05',
        'جون': '06',
        'جولائی': '07',
        'اگست': '08',
        'ستمبر': '09',
        'اکتوبر': '10',
        'نومبر': '11',
        'دسمبر': '12'
    }

    logging.info('%s', "SCRAPPING STARTED OF URDU POINT - URDU NEWS")
    url = "https://www.urdupoint.com/urdu-news"
    r = requests.get(url)

    article_data_dict = {}

    soup = BeautifulSoup(r.content, "html.parser")

    main_bar_div = soup.find("div", class_="main_bar fl")
    news_links = main_bar_div.find_all("a", class_="nshad_box small_news")

    for link in news_links:
        try:
            article_url = link["href"]
            response = requests.get(article_url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
            })

            if response.status_code == 200:
                logging.info('%s - %s', "Response status code: ", response.status_code)
                article_soup = BeautifulSoup(response.content, 'html.parser')

                h1_elements = article_soup.find('h1')
                if h1_elements is not None:
                    body_list = ''
                    for item in h1_elements:
                        body_list += item.text
                else:
                    logging.info('%s - %s', "H1 has no title: ", article_url)

                h2_elements = article_soup.find('h2')
                if h2_elements is not None:
                    title_h2 = ''
                    for item2 in h2_elements:
                        title_h2 += item2.text
                else:
                    logging.info('%s - %s', "H2 has no title: ", article_url)

                div_element = article_soup.find('div', class_='detail_txt urdu fs17 lh34 aj rtl')
                if div_element is not None:
                    article_story = ''
                    for article in div_element:
                        article_story += article.text
                else:
                    logging.info('%s - %s', "No div element with class 'detail_txt urdu fs17 lh34 aj rtl' found: ", article_url)

                time_date_author = article_soup.find('p', {'class': 'art_info_bar rtl ar urdu fs15 mb10'})
                if time_date_author is not None:
                    text = time_date_author.text
                    words = text.strip().split()  # Split the text into individual words

                    word_indices = {}
                    for index, word in enumerate(words):
                        word_indices[index] = word

                    # Extracting values based on different scenarios
                    if len(word_indices) == 8:
                        author_name = word_indices[0] + ' ' + word_indices[1] + ' ' + word_indices[2]
                        publish_time = word_indices[7]
                        publish_date = word_indices[6] + '-' + month_day_mapping[word_indices[5]] + '-' + word_indices[4]

                    elif len(word_indices) == 7:
                        author_name = word_indices[0] + ' ' + word_indices[1]
                        publish_time = word_indices[6]
                        publish_date = word_indices[5] + '-' + month_day_mapping[word_indices[4]] + '-' + word_indices[3]

                    elif len(word_indices) == 6:
                        author_name = word_indices[0]
                        publish_time = word_indices[5]
                        publish_date = word_indices[4] + '-' + month_day_mapping[word_indices[3]] + '-' + word_indices[2]

                    elif len(word_indices) == 5:
                        author_name = 'اردوپوائنٹ'
                        publish_time = word_indices[4]
                        publish_date = word_indices[3] + '-' + month_day_mapping[word_indices[2]] + '-' + word_indices[1]

                    else:
                        print('Lenth not match')
                        logging.info('%s - %s', "Length no match: ", body_list)

                time_obj = datetime.datetime.strptime(publish_time, "%H:%M")
                publish_time_fomatted = time_obj.strftime("%I:%M %p")

                # Get the image from link
                image_tag = article_soup.find('figure', class_='ac primaryimage')
                if image_tag is not None:
                    image_tag = image_tag.find('img')
                    if image_tag:
                        image_link =image_tag['src']
                        image_data = requests.get(image_link).content
                        image_name =os.path.basename(image_link)
                        image_folder =os.path.join(os.getcwd(), 'data', publish_date.replace('-', '/'), 'Urdu News', 'images')
                        os.makedirs(image_folder, exist_ok=True)
                        image_name_title = re.sub(r'[<>:"/\\|?*]', '', body_list[0:121])
                        image_path = os.path.join(image_folder, f'{image_name_title}.jpg'.replace('\r',''))
                        
                        if os.path.exists(image_path):
                            logging.info('%s - %s', "Image already exists: ", body_list)

                        else:
                            with open(image_path, 'wb') as f:
                                f.write(image_data)
                            logging.info('%s - %s', "Image downloaded ", body_list)


                        # Get the relative path from the base directory
                        image_path_short = '/'.join(image_path.split(os.sep)[5:]) # convert os.sep to '/'
                    else:
                        image_path_short = None
                else:
                    image_path_short= None

                # Create a dictionary with the article data
                article_data = {
                    'Article_Headline': body_list.replace('\r',''),
                    'Article_Story':  title_h2+' '+ article_story.replace('\n',''),
                    'Article_Author': author_name,
                    'Article_Publish_date': publish_date,
                    'Atricle_Publish_time': publish_time_fomatted,
                    'Article_url': article_url,
                    'Article_Scraped': True,
                    'Batch': False,
                    'article_image_url': image_path_short
                }
                # Append the article data to the dictionary for this date
                if publish_date not in article_data_dict:
                    article_data_dict[publish_date] = {
                        'Channel Name': 'Urdu News',
                        'Webite_url': url,
                        'Articles': []
                    }
                article_data_dict[publish_date]['Articles'].append(article_data)

                # Save the JSON file if the article is present
                if body_list:
                    folder_path = os.path.join(os.getcwd(), 'data', publish_date.replace('-', os.sep),
                                               'Urdu News')
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
                            'Channel Name': 'Urdu Point',
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
