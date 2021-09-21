import csv
import datetime
import time
import os
from dotenv import load_dotenv

from selenium import webdriver

load_dotenv()

base_url = "https://stratechery.com/category/"
main_url = 'https://stratechery.com'
daily = {
    "file": "data.csv",
    "url": base_url + 'daily-email/page/',
    "type": "DailyUpdate",
    "page": 100}
article = {
    "file": "article.csv",
    "url": base_url + 'articles/page/',
    "type": "Article",
    "page": 47}


def set_driver():

    options = webdriver.ChromeOptions()  # Set up Chinese
    # options.add_argument('--headless')
    options.add_argument('lang=zh_CN.UTF-8')  # Replacement of head
    options.add_argument(
        'User-Agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"')
    driver = webdriver.Chrome(
        os.getenv('DRIVER_PATH'),
        options=options)

    driver.get(main_url)
    driver.add_cookie({"name": "atomic_verifier",
                      "value": os.getenv('VERIFIER')})
    driver.add_cookie({"name": "atomic_token", "value": os.getenv("TOKEN")})

    return driver


def get_page_data():
    # get title
    title_list = driver.find_elements_by_class_name('entry-title')

    # get date
    meta_list = driver.find_elements_by_class_name('entry-meta')
    date_list = []
    for meta in meta_list:
        date_list.append(
            meta.find_element_by_class_name('entry-date').text)

    # get content
    content_list = driver.find_elements_by_class_name('entry-content')

    # get link
    link_list = []
    for title in title_list:
        link_list.append(
            title.find_element_by_tag_name('a').get_attribute('href'))

    return title_list, date_list, content_list, link_list


def init_csv(file_name, update):
    if update:
        f = open(file_name, "w+")
        f.close()
    else:
        with open(file_name, 'w') as out_file:
            write = csv.writer(out_file)
            header = ['Title', 'Date', 'Type',
                      'Read', 'Digest', 'Content', 'Link']
            write.writerow(header)


def write_csv(obj, title_list, date_list, content_list, link_list, last_date=""):
    if last_date:
        print("update mode")

    file_name = obj['file']
    type = obj['type']

    with open(file_name, 'a') as f:
        write = csv.writer(f)
        for title, date, content, link in zip(title_list, date_list, content_list, link_list):
            current_date = date_parser(date)
            if last_date and last_date >= current_date:
                print("last: ", last_date,
                      " current: ", current_date)
                return True
            line = [title.text, current_date,
                    type, "False", "", content.text, link]
            write.writerow(line)


def date_parser(date):
    # Thursday, August 12, 2021
    date_list = date.replace(',', '').split()
    days_of_week = date_list[0]
    month_name = date_list[1]
    month = str(datetime.datetime.strptime(month_name, "%B").month)
    day = date_list[2]
    year = date_list[3]
    return "/".join([year, month, day])


def get_last_date(file_name):
    with open(file_name) as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            if idx == 1:
                return row[1]
    print("file is empty")
    return ""


def process_data(obj, driver, update):
    last_date = get_last_date(obj['file'])
    init_csv(obj['file'], update)

    for page_num in range(1, obj['page']):
        web_url = obj['url'] + str(page_num) + '/'
        driver.get(web_url)

        if update:

            uptodate = write_csv(obj, *get_page_data(), last_date)
            if uptodate:
                return
        else:

            write_csv(obj, *get_page_data(), last_date)
        time.sleep(1)


def data_exists(obj):
    if get_last_date(obj['file']):
        print("data exists: True")
        return True
    print("data exists: False")
    return False


if __name__ == '__main__':

    driver = set_driver()
    print("finish setting")
    
    # daily
    update = data_exists(daily)
    print("Update: ", update)
    process_data(daily, driver, update)

    # article
    update = data_exists(article)
    print("Update: ", update)
    process_data(article, driver, update)
