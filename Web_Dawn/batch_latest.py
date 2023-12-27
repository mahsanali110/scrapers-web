# Importing Libraries
import time as t
import json
import os
import re
from datetime import datetime
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

    def main(self):
        try:
            self.create_log()
            if not os.path.exists("token.txt"):
                self.get_token()

            with open("token.txt") as f:
                token = f.read()

            headers = {"Authorization": "Bearer " + token}

            main_folder = 'data'
            api_url_web = config["api_url_web"]

            current_date = datetime.now().strftime("%Y-%m-%d")
            path = current_date.split('-')
            json_path = main_folder + '/' + path[0] + '/' + path[1] + '/' + path[2] + '/content.json'

            if os.path.exists(json_path):
                json_file = json.load(open(json_path, 'r'))
                for category in json_file:
                    for art in json_file[category]['articles']:
                        if art['batch'] is False and art['article_date'] and art['article_headline'] \
                                and art['article_date'] and art['article_time'] and art['article_story'] \
                                and art['article_author']:

                            headline = art['article_headline']
                            date = art['article_date']
                            time = art['article_time']
                            story = art['article_story']
                            author = art['article_author']
                            url = art['article_url']

                            date = "/".join(date.split("/")[::-1])
                            head, story = self.trim(headline, story)
                            if story == '':
                                story = "Nothing Scrapped"
                            if not os.path.exists(os.getcwd() + '/' + art['article_image_path']):
                                file = ('files', "")
                                self.files.append(file)
                            elif os.path.exists(os.getcwd() + '/' + art['article_image_path']):
                                if art['article_image_path'] != '':
                                    file = ('files', open(os.getcwd() + '/' + art['article_image_path'], 'rb'))
                                    self.files.append(file)
                                else:
                                    file = ('files', art['article_image_path'])
                                    self.files.append(file)
                            json_data = ('data', json.dumps(
                                self.create_json('The Dawn', author, date, time, story, art['article_image_path'],
                                                 head,
                                                 url)))
                            self.batch.append(json_data)

            if len(self.files) and len(self.batch) > 0:
                batch_log.info('%s - %s - %s', "BATCH SIZE ", len(self.files), len(self.batch))
                if len(self.files) and len(self.batch) > 1000:
                    self.files = self.files[:1000]
                    self.batch = self.batch[:1000]
                    batch_log.info('%s - %s - %s', "BATCH SIZE LIMIT", len(self.files), len(self.batch))
                response = self.send_response(api_url_web, headers, self.files, self.batch)
                response_content = json.loads(response.content.decode('utf-8'))
                if response.status_code == 201:
                    json_path = main_folder + '/' + path[0] + '/' + path[1] + '/' + path[2] + '/content.json'
                    if os.path.exists(json_path):
                        json_file = json.load(open(json_path, 'r'))
                        for category in json_file:
                            for res_con in response_content:
                                if res_con['status'] == 201:
                                    for art in json_file[category]['articles']:
                                        if art['batch'] is False and art['article_url'] == res_con['jobIdentifier']:
                                            art['batch'] = True
                                            break
                                else:
                                    batch_log.info('%s - %s -%s', "WEB RESPONSE FROM CLIENT",
                                                   res_con['status'], res_con['message'])
                        with open(json_path, "w") as out_file:
                            json.dump(json_file, out_file)
                        batch_log.info('%s', "WEB BATCH SENT SUCCESSFULLY")
                else:
                    batch_log.info('%s - %s', "RESPONSE FROM CLIENT", response)
            else:
                batch_log.info('%s - %s - %s', "BATCH SIZE ", len(self.files), len(self.batch))

        except Exception as excep:
            batch_log.info('%s - %s', "EXCEPTION", excep)
            pass
