from bs4 import BeautifulSoup
import requests
import datetime
import json
import os.path
import logging

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
        day_folder_path = project_directory + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(
            log_day[1])
        day_folder_file = os.path.isdir(day_folder_path)
        day_path = project_directory + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(
            log_day[1]) + "/job.log"
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


def dawn_english(date_string):
    try:
        create_log()
        base_directory = os.path.dirname(os.path.abspath(__file__))
        project_directory = os.path.join(base_directory)
        date = date_string.split('-')
        subdir1 = "data"
        subdir2 = str(date[0])
        subdir3 = str(date[1]).zfill(2)
        subdir4 = str(date[2]).zfill(2)
        subdir5 = "images"
        dir_path = os.path.join(subdir1, subdir2, subdir3, subdir4, subdir5)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = project_directory + '/' + 'data' + '/' + date[0] + '/' + date[1] + '/' + date[
            2] + '/' + "content.json"
        categories = dict()

        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                categories = json.load(f)
        else:
            url = "https://www.dawn.com/newspaper"
            response = requests.get(url)
            if response.status_code == 200:
                htmlContent = response.content
                soup = BeautifulSoup(htmlContent, 'html.parser')

                nav_bar_elements = soup.find('nav',
                                             class_="border-t-2 border-solid border-black font-arial text-2.5 font-bold uppercase cursor-pointer").find_all('a')
                for element in nav_bar_elements:
                    if response.status_code == 200:
                        category_name, url = (element.text, element['href'])
                        if category_name == 'Web Archive':
                            category_url = "https://www.dawn.com" + '/'.join(
                                url.split('/')[:-1]) + '/' + 'latest-news' + "/"
                        else:
                            category_url = "https://www.dawn.com" + '/'.join(url.split('/')[:-1]) + "/"

                        categories[category_name.strip()] = dict(category_name='',
                                                                 category_url='',
                                                                 category_is_scrapped='',
                                                                 articles=[])
                        categories[category_name.strip()]['category_name'] = category_name.strip()
                        categories[category_name.strip()]['category_url'] = category_url
                        categories[category_name.strip()]['category_is_scrapped'] = False
                        logging.info('%s - %s', "CATEGORY SCRAPPED", category_name.strip())

                    with open(file_path, 'w') as f:
                        json.dump(categories, f)

        return categories
    except Exception as exception:
        logging.info('%s - %s', "EXCEPTION", exception)
