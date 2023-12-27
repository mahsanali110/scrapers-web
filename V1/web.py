# Importing Libraries
import time
import json
import re
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
from pathlib import Path
import logging
#
# import batch_latest


# import proxies
class arr():
    def __init__(self):
        self.batch = []
        self.files = []


class Scrappers:

    def __init__(self, k, v):
        try:
            self.news = k
            self.website_url = v['website_url']
            self.json_file = v['json_file']
            self.content_json = v['content_json']
            self.parent = v['parent']
            self.category = v['category_name']
            self.ele_type = v['element_soup_type']
            self.ele_div = v['element_soup_class']
            self.href_div = v['href_div']
            self.art_typ = v['article_soup_type']
            self.art_div = v['article_soup_div']
            self.body_type = v['body_type']
            self.body_div = v['body_div']
            self.author_type = v['author_type']
            self.author_div = v['author_div']
            self.title_type = v['title_type']
            self.title_div = v['title_div']
            self.date_type = v['date_type']
            self.date_div = v['date_div']
            self.image_div = v['image_div']
            self.mainfolder = "/main_json/"
            self.months = {'جنوری': "January",
                           'فروری': "February",
                           'مارچ': "March",
                           'اپریل': "April",
                           'مئی': "May",
                           'جون': "June",
                           'جولائی': "July",
                           'اگست': "August",
                           'ستمبر': "September",
                           'اکتوبر': "October",
                           'نومبر': "November",
                           'دسمبر': "December"},
            self.response = requests.get(self.website_url)
            self.soup = bs(self.response.content, 'html.parser')
            self.base_directory = os.path.dirname(os.path.abspath(__file__))
            self.project_directory = os.path.join(self.base_directory)
            self.header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/98.0.4758.102 Safari/537.36'}


        except Exception as excep:
            logging.info('%s - %s', "ERROR IN GETTING THE WEBISTES URL", excep)

    # Function to get all the categories we want to scrap

    def month_converter(self, month):
        months = ['جنوری', 'فروری', 'مارچ', 'اپریل', 'مئی', 'جون', 'جولائی', 'اگست', 'ستمبر', 'اکتوبر', 'نومبر',
                  'دسمبر']
        return months.index(month) + 1

    def hr_converter(self, time):
        if time == 'صبح':
            time = time.replace("صبح", "AM")
        if time == 'شام':
            time = time.replace("شام", "PM")
            return time

    def get_scrapped_data(self):
        try:
            Path(self.project_directory + self.mainfolder).mkdir(parents=True, exist_ok=True)
            file_exists = os.path.exists(self.project_directory + self.mainfolder + self.json_file)

            if not file_exists:
                dictionary = dict()

                dictionary[self.category] = {
                    'category_name': self.category,
                    'category_url': self.website_url,
                    'is_scrapped': False,
                    'scrapped_date': datetime.now().strftime("%d/%m/%Y")}

                logging.info('%s', "MAIN JSON FILE CREATED SUCCESSFULLY")

            else:
                with open(self.project_directory + self.mainfolder + self.json_file, 'r') as jf:
                    dictionary = json.load(jf)
                dictionary[self.category]['scrapped_date'] = datetime.now().strftime("%d/%m/%Y")

                logging.info('%s', "MAIN JSON FILE ALREADY EXISTS")

            scrappers.get_category_links(dictionary)

            return True

        except Exception as excep:
            logging.info('%s - %s', "ERROR: EXCEPTION WHILE GETTING NEWS CATEGORIES", excep)

    # Function to Extract the Links

    def get_category_links(self, dictionary):
        try:
            for k, v in dictionary.items():
                if k == self.category:
                    if not 'articles' in v.keys():
                        v['is_scrapped'] = True
                        v['articles'] = []
                        ref = []
                    else:
                        ref = []
                        for refer in v['articles']:
                            ref.append(refer['article_url'])

                    url = v['category_url']
                    response = requests.get(url, headers=self.header)
                    soup = bs(response.content, 'html.parser')

                    if self.news == "Daily Times Pakistan" or self.news == "Business Recorder":
                        elements = soup.find_all(self.ele_type)
                    else:
                        elements = soup.find_all(self.ele_type, {"class": self.ele_div})

                    if len(elements) < 10:
                        elements = soup.find(self.ele_type, {'class', self.ele_div}).find_all('li')
                        if len(elements) == 0:
                            elements = soup.find(self.ele_type, {'class', self.ele_div}).find_all('div')
                    # print(len(ref))
                    scrappers.get_article_data(dictionary, elements, ref)
            logging.info('%s', "NEWS CATEGORY LINKS EXTRACTED SUCCESSFULLY")

            return True

        except Exception as excep:
            logging.info('%s-%s', "ERROR: EXCEPTION WHILE GETTING NEWS CATEGORIES LINKS ", excep)

    # Function to Extract the Data for Every Article

    def get_article_data(self, dictionary, elements, ref):
        try:
            # print(ref)
            for element in elements:
                if self.href_div == "":
                    if self.news == '92 News':
                        href = element.find('a')['href']
                        href = 'https://92newshd.tv' + href
                    else:
                        try:
                            if element.find('a') != None:
                                href = element.find('a')['href']
                            else:
                                pass
                        except:
                            pass
                else:
                    try:
                        href = element.find('a', self.href_div)['href']
                    except:
                        pass

                if href not in ref:
                    logging.info(href)
                    ref.append(href)

                    try:
                        response = requests.get(href, headers=self.header)
                    except Exception as excep:
                        logging.info('%s - %s', "WARNING: ARTICLE LINK IS DOWN NOW", excep)
                        continue

                    if response.status_code == 200:
                        logging.info("LINK IS RESPONSIVE")
                        article_dictionary, content_dictionary, content_file_path = scrappers.get_data(href, response,
                                                                                                       element)
                        check = True

                    else:
                        check = False
                        for i in range(5):
                            logging.info("RETRYING")
                            if check == False:
                                try:
                                    response = requests.get(href, headers=self.header)
                                except Exception as excep:
                                    logging.info('%s', "WARNING: LINK IS STILL DOWN", )
                                    continue

                                if response.status_code == 200:
                                    logging.info("LINK IS RESPONSIVE NOW")
                                    article_dictionary, content_dictionary, content_file_path = scrappers.get_data(href,
                                                                                                                   response,
                                                                                                                   element)
                                    check = True
                            else:
                                break

                    if check:
                        if article_dictionary is not False:
                            dictionary[self.category]['articles'].insert(0, article_dictionary)
                            file_exists = os.path.exists(content_file_path + self.content_json)

                            if not file_exists:
                                file = open(content_file_path + self.content_json, 'w')
                                content = dict()
                                content['articles'] = []

                            else:
                                with open(content_file_path + self.content_json, 'r') as jf:
                                    content = json.load(jf)

                            content['articles'].insert(0, content_dictionary)

                            with open(content_file_path + self.content_json, 'w') as fp:
                                json.dump(content, fp, default=str)

                            logging.info('%s', "SCRAPED SUCCESSFULLY")
                        else:
                            logging.info('%s', "SCRAPPING FAILED")
                            pass
                    else:
                        logging.info('%s', "SCRAPPING FAILED")
                        pass

                else:
                    pass

            with open(self.project_directory + self.mainfolder + self.json_file, 'w') as fp:
                json.dump(dictionary, fp, default=str)

            return True

        except Exception as excep:
            logging.info('%s - %s', "SCRAPPING FAILED", excep)

    def get_url_and_create_dir(self, date, status):
        date_list = date.split('-')
        if status == "content":
            file_path = self.project_directory + self.parent + date_list[0] + '/' + date_list[1] + '/' + date_list[
                2] + '/Scrape/'
        elif status == "image":
            file_path = self.project_directory + self.parent + date_list[0] + '/' + date_list[1] + '/' + date_list[
                2] + '/Scrape/' + 'images/'
        elif status == 'image_path_json':
            file_path = self.parent + date_list[0] + '/' + date_list[1] + '/' + date_list[
                2] + '/Scrape/' + 'images'
            return file_path

        Path(file_path).mkdir(parents=True, exist_ok=True)

        return file_path

    def get_data(self, href, response, element):
        try:
            soup = bs(response.content, 'html.parser')
            article_soup = soup.find(self.art_typ, self.art_div)

            if article_soup is None:
                article_soup = soup.find(self.art_typ)
            if self.news == 'Jurat':
                article_soup = soup
            if article_soup:
                body = scrappers.get_body(article_soup)
                author = scrappers.get_author(article_soup)
                title = scrappers.get_title(article_soup)
                date, time = scrappers.get_date_time(article_soup)
                logging.info('%s - %s', "date of scrapped article is ", date)
                content_file_path = scrappers.get_url_and_create_dir(date, "content")
                image_file_path = scrappers.get_url_and_create_dir(date, "image")
                image_local_path = scrappers.get_image(article_soup, image_file_path, title)
                if image_local_path != '':
                    img_path = os.path.join(scrappers.get_url_and_create_dir(date, "image_path_json"), os.path.basename(image_local_path))
                else:
                    img_path = image_local_path

                article_dictionary = {
                    'newspaper': self.news,
                    'headline': title,
                    'article_url': href,
                    'article_date': "/".join(date.split("-")[::-1]),
                    'article_time': time,
                    'content_path': content_file_path + self.content_json,
                    'image_path': img_path,
                    'article_is_scrapped': True
                }

                content_dictionary = {
                    'url': href,
                    'article_date': "/".join(date.split("-")[::-1]),
                    'article_time': time,
                    'headline': title,
                    'story': body,
                    'author': author,
                    'image_path': img_path,
                    'newspaper': self.news,
                    'status': False
                }

                return article_dictionary, content_dictionary, content_file_path

            else:
                return False, False, False
        except Exception as exception:
            logging.info('%s - %s', "ERROR IN GETTING DATA", exception)

    # Get Body Function

    def get_body(self, article_soup):
        try:
            if self.body_type == "p":
                try:
                    if self.news == 'Daily Dunya News' or self.news == 'Business Recorder':
                        body = article_soup.find('article').find_all('p')
                    if self.news == 'Jasarat':
                        body = article_soup.find_all('p')
                    else:
                        body = article_soup.find('div', self.body_div).find_all('p')
                except:
                    # body = article_soup.find_all('p', self.body_div)
                    body = article_soup.text

                body = " ".join([line.text.strip() for line in body])

            elif self.body_type == "span":
                body = article_soup.find(self.body_type, self.body_div).find_all('p')
                body = " ".join([line.text.strip() for line in body])

            elif self.body_type == "b":
                body = article_soup.find('div', self.body_div).text.strip().replace("\n", "")
            # elif self.body_type == 'article':
            #     body = article_soup.find_all('p').text.strip()

            if body == "":
                body = article_soup.find('div', self.body_div).text.strip().replace("\n", "")

        except:
            body = ""

        return body

    # Get Author Function

    def get_author(self, article_soup):
        try:
            if self.news == "The Express Tribune":
                author = article_soup.find(self.author_type, self.author_div).text.strip()
                author = author.split("\n")[0].strip()
            elif self.news == "Hum News":
                author = article_soup.find(self.author_type, self.author_div).nextSibling.strip()
                author = author.split("\n")[0].strip()
            elif self.news == 'Daily Dunya News':
                author = 'daily_dunya'
            elif self.news == '92 News':
                author = '92 News'
            elif self.news == 'Financial Daily' or self.news == "Financial Daily General":
                author = article_soup.find(self.author_type, self.author_div).find('a').text
            elif self.news == "Jurat":
                author = article_soup.find(self.author_type, self.author_div).contents[2].strip()
            else:
                author = article_soup.find(self.author_type, self.author_div).text.strip()
        except:
            author = ""

        return author

    # Get Title Function

    def get_title(self, article_soup):
        try:
            if self.title_type == "div":
                title = article_soup.find(self.title_type, self.title_div).text.strip()
            else:
                title = article_soup.find(self.title_type).text.strip()
        except:
            title = ""

        return title

    # Get Date Time Function

    def get_date_time(self, article_soup):
        try:
            date = article_soup.find(self.date_type, self.date_div).text.strip()
            time = "12:00AM"

            if self.news == "The Dawn":
                time = date.replace("\n", " ").split(" ")[3]
                date = " ".join(date.replace("\n", " ").split(" ")[:3])
                if "am" in time:
                    time = time.replace("am", "AM")
                elif "pm" in time:
                    time = time.replace("pm", "PM")

            elif self.news == "The Express Tribune":
                date = date.split("\n")[1].strip()

            elif self.news == "Global Times":
                time = " ".join(date.split(" ")[4:6]).replace(" ", "")
                date = date.split(" ")[1:4]
                date[0] = datetime.strptime(date[0], '%b').strftime('%B')
                date = " ".join(date)

            elif self.news == "The Nation" or self.news == 'Daily Pakistan':
                if "|" in date:
                    if self.news == 'Daily Pakistan':
                        time = date.split("|")[1].strip()
                        date = date.split("|")[0].strip()
                        t1 = time[0:5]
                        t2 = time[6:8]
                        time = t1 + t2.strip()
                    else:
                        time = date.split("|")[0].strip().replace(" ", "")
                        date = date.split("|")[1].strip()

            elif self.news == "Jang News":
                date_chk = article_soup.find_all('div', {'class', 'detail-time'})
                for i in date_chk:
                    try:
                        if i.find('a')['href']:
                            pass
                    except:
                        date = i.text.strip()
                date = date.split("،")
                year = date[1].strip()
                month = self.months[date[0].strip().split(" ")[1]]
                day = date[0].strip().split(" ")[0]
                date = month + " " + day + ", " + year

            elif self.news == "Daily Express News":
                date = date[4:]
                month = self.months[date[2:9]]
                year = date[10:]
                day = date[:2]
                date = month + " " + day + ", " + year

            elif self.news == "BBC Urdu":
                month = self.months[date[3:9]]
                year = date[10:]
                day = date[:2]
                date = month + " " + day + ", " + year

            elif self.news == "The Nawaiwaqt":
                date = date.split("  ")[1].strip()
                time = date.split(",")[0].replace(" ", "")
                date1 = date.split(",")[1]
                month = date1.split(" ")[1]
                day = date1.split(" ")[2]
                year = date.split(",")[2].replace(" ", "")
                date = month + " " + day + ", " + year
            elif self.news == "Jasarat":
                new_date = (article_soup.find(self.date_type, self.date_div).text.strip()).split(',')
                time = new_date[-1]
                date = str(re.sub(r"[\n\t\s]*", "", str(new_date[1]))) + "-" + str(
                    datetime.strptime(new_date[0].split(' ')[0], '%B').month) + "-" + str(
                    new_date[0].split(' ')[1])
                return date, time
            elif self.news == 'Daily Ummat':
                new_date = ((article_soup.find(self.date_type, self.date_div)).next).split(' ')
                time = new_date[5].split()[0]
                time = self.hr_converter(time)
                time = str(new_date[4]) + " " + str(time)
                date = str(new_date[3].split(',')[0]) + "-" + str(self.month_converter(new_date[2])) + "-" + str(
                    new_date[1])
                return date, time
            elif self.news == 'Financial Daily' or self.news == "Financial Daily General":
                new_date = ((article_soup.find(self.date_type, self.date_div)).text).split(',')
                date = str(re.sub(r"[\n\t\s]*", "", str(new_date[2]))) + '-' + str(
                    datetime.strptime(new_date[1].split(' ')[1], '%B').month) + '-' + str(new_date[1].split(' ')[2])
                time = "12:00AM"
                return date, time
            # elif self.news == 'Jurat':
            #     date = article_soup.find(self.author_type, self.author_div).contents[6].strip().split(',')[1]
            #     date =
            #     time = "12:00AM"
            if self.news == 'Daily Pakistan':
                date = datetime.strptime(date, "%b %d, %Y")
            else:
                date = datetime.strptime(date, "%B %d, %Y")
        except:
            date = str(datetime.now()).split(" ")[0]
            time = "12:00AM"

        return str(date).split(" ")[0], time

    # Get Image Function

    def get_image(self, article_soup, image_file_path, title):
        try:
            if self.news == "The Express Tribune" or self.news == "Hum News" or self.news == "Daily Express News" or self.news == "Daily Times Pakistan" or self.news == "The Nawaiwaqt" or self.news == 'Daily Pakistan' or self.news == 'Daily Dunya News' or self.news == 'Geo News' or self.news == '92 News' or self.news == 'Business Recorder' or self.news == 'Jasarat' or self.news == 'Daily Ummat' or self.news == 'Financial Daily' or self.news == "Financial Daily General"or self.news == 'Jurat':
                image_div = article_soup.find("div", self.image_div)
            else:
                image_div = article_soup.find(self.image_div)

            if image_div:
                if self.news == "The Express Tribune":
                    image_url = image_div.find('img')['data-src']
                elif self.news == "Daily Times Pakistan":
                    image_url = image_div.find('img')['data-lazy-src']
                else:
                    image_url = image_div.find('img')['src']
                img_data = requests.get(image_url, headers=self.header).content
                image_local_path = image_file_path + title.strip() + '.jpeg'
                with open(image_local_path, 'wb') as handler:
                    handler.write(img_data)
                handler.close()

            else:
                image_local_path = ""

        except Exception as excep:
            image_local_path = ""
            pass

        return image_local_path

    # Logging Function

    def create_log(self):
        try:
            x = datetime.now()
            year = x.strftime("%Y")
            month = x.strftime("%B")
            day = x.strftime("%x")
            log_day = day.split("/")
            log_path = self.project_directory + "/" + "log"
            log_file = os.path.isdir(log_path)
            year_path = self.project_directory + "/" + "log" + "/" + str(year)
            year_file = os.path.isdir(year_path)
            month_path = self.project_directory + "/" + "log" + "/" + str(year) + "/" + str(month)
            month_file = os.path.isdir(month_path)
            day_folder_path = self.project_directory + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(
                log_day[1])
            day_folder_file = os.path.isdir(day_folder_path)
            day_path = self.project_directory + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(
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
            return
        except Exception as excep:
            logging.info('%s - %s', "LOG DID NOT CREATED SUCCESSFULLY", excep)


# Getting Configuration File

# start_time = perf_counter()

# Calling Functions of Scrapper Class with Threading
with open('config.json', 'r') as jf:
    config = json.load(jf)
# threads = []
# proxy = proxies.proxy()
while True:
    for k, v in config.items():
        scrappers = Scrappers(k, v)
        scrappers.create_log()
        logging.info('%s - %s', "SCRAPING START", k)
        scrappers.get_scrapped_data()
        logging.info('%s - %s', "SCRAPING END", k)
        # print("done")
        # t = Thread(target=scrappers.get_scrapped_data)
        # threads.append(t)
        # t.start()
    # time.sleep(1800)

