# Importing Libraries
import time
import time as t
import json
import os
import re
from pathlib import Path
from datetime import datetime
import shutil
import logging as batch_log
import requests
from langdetect import detect

config = json.load(open('batch_config.json', 'r'))


# Batch Generator Class

class BatchGenerator:

    def __init__(self):
        self.base_directory = os.path.dirname(os.path.abspath(__file__))
        self.project_directory = os.path.join(self.base_directory)
        self.path = os.path.join(self.project_directory, "web", "")
        self.art_cnt = 0
        # self.fail_path = self.project_directory + '/failed/'
        # self.csv_path2 = self.fail_path + 'failed_jobs_batch.csv'
        self.batch = []
        self.files = []
        # Path(self.fail_path).mkdir(parents=True, exist_ok=True)

    def send_response(self, api_url_web, headers, files, data):
        max_retries = 5
        retry_index = 0
        while retry_index < max_retries:
            try:
                response = requests.post(api_url_web, headers=headers, files=files, data=data)
                if response.status_code == 201:
                    batch_log.info('%s', "RESPONSE SENT SUCCESSFULLY")
                    return response
                else:
                    batch_log.info('%s - %s - %s -%s', "RESPONSE IS NOT 201", api_url_web,
                                   " TRIED: " +
                                   str(retry_index + 1) + "/" + str(max_retries) + " TIMES.", response.status_code)
                    retry_index += 1
                    t.sleep(10)
            except Exception as excep:
                batch_log.info('%s - %s - %s - %s', "EXCEPTION OCCURRED WHILE SENDING RESPONSE ", api_url_web,
                               " TRIED: " +
                               str(retry_index + 1) + "/" + str(max_retries) + " TIMES.", excep)
                retry_index += 1
        return None

    def get_token(self):
        try:
            url = config['url_auth']
            data = config['user_data']
            response = requests.post(url, data)
            if response.status_code == 400:
                return response.status_code
            token = json.loads(response.content)['tokens']['access']['token']
            with open("token.txt", "w") as f:
                f.write(token)
            batch_log.info('%s', "TOKEN GENERATED")
        except Exception as excep:
            batch_log.info('%s - %s', "TOKEN DID NOT GENERATE DUE TO ERROR OF USER LOGGED IN", excep)

    def create_json(self, news, author, date, time, story, image, head, url):
        language = detect(story)
        if language == 'en':
            language = 'ENGLISH'
        elif language == 'ur':
            language = 'URDU'
        json_data = {
            "jobIdentifier": url,
            "source": "Blog",
            "channel": news,
            "platform": 'Blog',
            "language": language,
            "region": "National",
            "priority": "HIGH",
            "comments": '',
            "publisher": author,
            "guests": [{}],
            "programName": head,
            "programType": 'Article',
            "programDate": date,
            "programTime": time,
            "thumbnailPath": image,
            "videoPath": "",
            "topic1": "",
            "topic2": "",
            "topic3": "",
            "hashtags": "",
            "transcription": [{
                "duration": '',
                "speaker": '',
                "line": story

            }]
        }
        return json_data

    def getting_folders(self, filename):
        self.data_getting(filename)

    def find_index(self, dicts, key, value):
        class Null:
            pass

        for i, d in enumerate(dicts):
            if d.get(key, Null) == value:
                return i
        else:
            raise ValueError('no dict with the key and value combination found')

    def data_getting(self, filename):
        try:
            self.create_log()
            if not os.path.exists("token.txt"):
                self.get_token()

            with open("token.txt") as f:
                token = f.read()

            headers = {"Authorization": "Bearer " + token
                       }
            api_url_web = config["api_url_web"]
            for f1 in filename:
                data_config = json.load(open(f1, 'r'))
                for art in data_config['articles']:
                    if art['status'] is False and art['newspaper'] and art['headline'] and art['article_date'] and \
                            art['article_time'] != '':
                        story = str(art['story'].strip().replace("\n", " "))
                        head = art['headline']
                        date = art['article_date']
                        date = "/".join(date.split("/")[::-1])
                        time = art['article_time']
                        author = art['author']
                        url = art['url']
                        head, story = self.trim(head, story)
                        if story == '':
                            story = "Nothing Scrapped"
                        if not os.path.exists(os.getcwd() + art['image_path']):
                            file = ('files', "")
                            self.files.append(file)
                        elif os.path.exists(os.getcwd() + art['image_path']):
                            if art['image_path'] != '':
                                file = ('files', open(os.getcwd() + art['image_path'], 'rb'))
                                self.files.append(file)
                            else:
                                file = ('files', art['image_path'])
                                self.files.append(file)
                        json_data = ('data', json.dumps(
                            self.create_json(art['newspaper'], author, date, time, story, art['image_path'], head,
                                             url)))
                        self.batch.append(json_data)
            if len(self.files) and len(self.batch) > 0:
                batch_log.info('%s - %s - %s', "BATCH SIZE ", len(self.files), len(self.batch))
                if len(self.files) and len(self.batch) > 1000:
                    self.files = self.files[:1000]
                    self.batch = self.batch[:1000]
                    batch_log.info('%s - %s - %s', "BATCH SIZE LIMIT", len(self.files), len(self.batch))
                response = self.send_response(api_url_web, headers, self.files, self.batch)
                if response.status_code == 201:
                    response_content = json.loads(response.content)
                    for f1 in filename:
                        data_config = json.load(open(f1, 'r'))
                        for res_con in response_content:
                            if res_con['status'] == 201:
                                for art in data_config['articles']:
                                    if art['status'] is False and res_con['jobIdentifier'] == art['url']:
                                        art['status'] = True
                                        break
                            else:
                                batch_log.info('%s - %s -%s', "WEB RESPONSE FROM CLIENT", res_con['status'],
                                               res_con['message'])
                        with open(f1, "w") as out_file:
                            json.dump(data_config, out_file)
                    batch_log.info('%s', "WEB BATCH SENT SUCCESSFULLY")
                else:
                    batch_log.info('%s - %s', "RESPONSE FROM CLIENT", response)
            else:
                batch_log.info('%s - %s - %s', "BATCH SIZE ", len(self.files), len(self.batch))

        except Exception as exception:
            batch_log.info('%s - %s', "ERROR IN EXECUTING DATA EXTRACTION FUNCTION", exception)

    # def send_client_response(self, api_url_web, headers, ticker_name, files, data):
    #     max_retries = 5
    #     retry_index = 0
    #     while retry_index < max_retries:
    #         try:
    #             response = requests.post(api_url_web, headers=headers, files=files, data=data)
    #             batch_log.info('%s - %s - %s', "RESPONSE SENT SUCCESSFULLY", ticker_name, 'COMPLETED')
    #             return response
    #
    #         except Exception as excep:
    #             batch_log.info('%s - %s - %s - %s', "EXCEPTION OCCURRED WHILE SENDING RESPONSE ", api_url_web,
    #                            " TRIED: " +
    #                            str(retry_index + 1) + "/" + str(max_retries) + " TIMES.", excep)
    #             retry_index += 1
    #             return None

    def path_generator(self, date, news, sta):
        if sta == "art":
            b_pth = os.path.join(self.path, news, date[0], date[1], date[2], "Batch", "")
            Path(b_pth).mkdir(parents=True, exist_ok=True)

        elif sta == "img":
            b_pth = os.path.join(self.path, news, date[0], date[1], date[2], "Scrape", "images", "")
            Path(b_pth).mkdir(parents=True, exist_ok=True)

        return b_pth

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
                log_day[1]) + "/Web_batch.log"
            if not log_file:
                os.mkdir(log_path)
            if not year_file:
                os.mkdir(year_path)
            if not month_file:
                os.mkdir(month_path)
            if not day_folder_file:
                os.mkdir(day_folder_path)
            batch_log.basicConfig(filename=day_path, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                                  level=batch_log.INFO, force=True)
            return batch_log
        except Exception as exception:
            batch_log.info('%s - %s', "LOG DID NOT CREATE", exception)

    def trim(self, head, body):
        head = re.sub(r'(?<!\n)\n(?!\n)', "", head)
        body = re.sub(r'(?<!\n)\n(?!\n)', "", body)

        return head, body

    def getAlldirInDiGui(self, path, resultList):
        filesList = os.listdir(path)
        for fileName in filesList:
            fileAbpath = os.path.join(path, fileName)
            if os.path.isdir(fileAbpath):
                self.getAlldirInDiGui(fileAbpath, resultList)
            else:
                if fileName == 'content.json':
                    resultList.append(fileAbpath)

    def main(self):
        try:
            json_list = []
            # news = []
            with open('config.json', 'r') as jf:
                config = json.load(jf)
            with open('batch_config.json', 'r') as j:
                b_config = json.load(j)
            for keys, values in b_config.items():
                batch_log = self.create_log()
                for k, v in config.items():
                    if keys == "channels":
                        for i in values:
                            if i == k:
                                # news.append(k)
                                PATH = os.getcwd() + '/web/' + k
                                if os.path.exists(PATH):
                                    self.getAlldirInDiGui(PATH, json_list)
                                    if len(json_list) == 0:
                                        continue
                                    else:
                                        batch_log.info('%s ', "BATCH START " + k)
                                        self.getting_folders(json_list)
                                        batch_log.info('%s ', "BATCH END " + k)
                                        time.sleep(3600)
                                else:
                                    continue
                            else:
                                PATH = os.getcwd() + '/web/' + k
                                if os.path.exists(PATH):
                                    self.getAlldirInDiGui(PATH, json_list)
                                    if len(json_list) == 0:
                                        continue
                                    else:
                                        batch_log.info('%s ', "BATCH START " + k)
                                        self.getting_folders(json_list)
                                        batch_log.info('%s ', "BATCH END " + k)

        except:
            pass
