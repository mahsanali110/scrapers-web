import datetime
import logging
import subprocess
import os
from signal import SIGKILL
import time


class Kill_Web:
    def get_file_count(self, filename):
        with open(filename, 'r') as fp:
            lines_count = len(fp.readlines())
            return lines_count

    def kill_processes(self, filename):
        try:
            current_file_dir = os.getcwd()
            bashCommand = "pgrep -f ." + current_file_dir + filename
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            output_list = output.strip().split()
            return output, output_list
        except Exception as exp:
            logging.info('%s - %s', 'EXCEPTION IN KILL PROCESS METHOD', exp)

    def create_log(self, day, year, month):
        try:
            log_day = day.split("/")
            log_path = os.getcwd() + "/" + "log"
            log_file = os.path.isdir(log_path)
            year_path = os.getcwd() + "/" + "log" + "/" + str(year)
            year_file = os.path.isdir(year_path)
            month_path = os.getcwd() + "/" + "log" + "/" + str(year) + "/" + str(month)
            month_file = os.path.isdir(month_path)
            day_folder_path = os.getcwd() + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(log_day[1])
            day_folder_file = os.path.isdir(day_folder_path)
            day_path = os.getcwd() + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(
                log_day[1]) + "/job_web_killing.log"
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
        except Exception as e:
            logging.info('%s - %s', 'EXCEPTION MAKING FOLDERS IN KILLING', e)

        return

    def main(self):
        while True:
            try:
                x = datetime.datetime.now()
                year = x.strftime("%Y")
                month = x.strftime("%B")
                day = x.strftime("%x")
                self.create_log(day, year, month)
                log_day = day.split("/")
                day_path = os.getcwd() + "/" + "log" + "/" + str(year) + "/" + str(month) + "/" + str(
                    log_day[1]) + "/job.log"
                file_count1 = self.get_file_count(day_path)
                time.sleep(900)
                file_count2 = self.get_file_count(day_path)
                if file_count2 == file_count1:
                    output, output_list = self.kill_processes("/web.py")
                    if len(output) != 0:
                        os.kill(int(output), SIGKILL)
                        logging.info("%s", "KILL PROCESSES OF TICKERS SAVING")
                        time.sleep(180)
            except Exception as e:
                logging.info('%s - %s', 'EXCEPTION MAKING FOLDERS IN KILLING', e)


tickers_killing = Kill_Web()
tickers_killing.main()
