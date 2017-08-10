import login
import requests
import csv
import random
import time
import socket
import http.client
import json
from bs4 import BeautifulSoup
import pymysql

try:
    import cookielib
except:
    import http.cookiejar as cookielib

#数据库连接
db = pymysql.connect('localhost','root','wj1312','zhihu',use_unicode=True, charset="utf8")
cursor = db.cursor()

#构建headers
agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.8',
    "Host": "www.zhihu.com",
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': agent,
    'Connection': 'keep-alive',
    'x-udid':'AJDC0Wn_LgyPTix8bD6HOfuNgcdh--rzr8Y=',
    'Referer':'https://www.zhihu.com/people/excited-vczh/following',
    'authorization':'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
}

number = 0


def get_content(url, data = None):
    timeout = random.choice(range(80,180))
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            status = response.status_code
            #response.encoding = "utf-8"
            break
        except socket.timeout as e:
            print("3:",e)
            time.sleep(random.choice(range(8,15)))
        except socket.error as e:
            print("4:",e)
            time.sleep(random.choice(range(20,60)))
        except http.client.BadStatusLine as e:
            print("S:",e)
            time.sleep(random.choice(range(30,80)))
        except http.client.IncompleteRead as e:
            print("6:",e)
            time.sleep(random.choice(range(5,15)))
    if status is 200:
        return response
    else:
        return None


def get_data_from_json(response):
    final = []
    html = response.json()
    data = html['data']

    for item in data:
        temp = []
        name = item['name']
        temp.append(name)
        url_token = item['url_token']
        temp.append(url_token)
        '''
        articles_count = item['articles_count']
        temp.append(articles_count)
        answer_count = item['answer_count']
        temp.append(answer_count)
        '''
        follower_count = item['follower_count']
        temp.append(follower_count)
        if follower_count >1000:
            final.append(temp)
    return final


def url_from_csv():
    file_name = 'user_data.csv'
    with open(file_name, 'r', errors='ignore', newline='')as f:
        f_csv = csv.DictReader(f)
        global number
        i = 0
        for row in f_csv:
            if i == number:
                url_token = row['url_token']
                number += 1
                break
            i = i + 1
    url = r'https://www.zhihu.com/api/v4/members/' + url_token + r'/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
    return url


def url_from_sql():
    print('url_from_sql')
    global db,cursor
    url_token = ' '
    sql = "SELECT * from user_list WHERE is_used=0"
    try:
        cursor.execute(sql)
        res = cursor.fetchone()
        url_token = res[2]
        sql = "UPDATE user_list SET is_used=1 WHERE url_token='%s'" % url_token
        cursor.execute(sql)
        db.commit()
    except:
        print('error fetch the url_token')
    url = r'https://www.zhihu.com/api/v4/members/' + url_token + r'/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
    return url


def url_switch(response):
    html = response.json()
    paging = html['paging']
    if paging['is_end'] is True:
        url = url_from_sql()
    else:
        url = paging['next']
    return url


def write_data(data):
    '''
    file_name = 'user_data.csv'
    #with的使用保证了在处理文件过程中无论是否发生异常，都能保证关闭
    with open(file_name,'a',errors='ignore',newline='')as f:
        fieldnames = ['name', 'url_token','articles_count', 'answer_count','follower_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        global number
        print(number)
        if number is 0:
            writer.writeheader()
            print("header is written")
            number = 1
        for item_data in data:
            writer.writerow({'name':item_data[0], 'url_token':item_data[1],  'articles_count':item_data[2],  'answer_count':item_data[3],'follower_count': item_data[4]})

    '''
    global cursor
    global db
    for item_data in data:
        try:
            sql = "INSERT IGNORE INTO user_list(name,url_token,follower_count) VALUES('%s','%s',%s)" % (item_data[0], item_data[1], item_data[2])
            cursor.execute(sql)
            db.commit()
        except:
            print('write data is fail')
            db.rollback()

if __name__ == '__main__':

    url = 'https://www.zhihu.com/api/v4/members/su-an-42-86/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
    while True:
        time.sleep(random.choice(range(1,4)))
        html = get_content(url)
        if html is None:
            url = url_from_sql()
            continue
        else:
            url = url_switch(html)
            user_data = get_data_from_json(html)
        if user_data is None:
            continue
        else:
            print(user_data)
            write_data(user_data)

