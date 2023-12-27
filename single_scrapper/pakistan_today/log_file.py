import logging
import os
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
                   + "/pakistan_today.log"
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