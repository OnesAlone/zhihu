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


db = pymysql.connect('localhost','root','wj1312','zhihu',use_unicode=True, charset="utf8")
cursor = db.cursor()

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

number = 1
id_number = 5799


def get_content(url, data = None):
    timeout = random.choice(range(80,180))
    while True:
        try:
            response = requests.get(url, headers =headers, timeout = timeout)
            status = response.status_code
            #print(status)
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
    temp = []
    html = response.json()
    education = ' '
    major = ' '
    company = ' '
    job = ' '
    location = ' '
    name = html.get('name',' ')
    gender = html.get('gender',' ')
    educations = html.get('educations',{})
    if educations is None:
        education = " "
    else:
        for edu in educations:
            education = edu.get('school',{'name':' '}).get('name')
            major = edu.get('major',{'name':' '}).get('name')
    employments = html.get('employments')
    for employment in employments:
        company = employment.get('company',{}).get('name'," ")
        job = employment.get('job',{}).get('name','')
    locations = html.get('locations',{})
    for loc in locations:
        location = loc.get('name','')
    description = html.get('description','')
    headline = html.get('headline','')
    following_count = html.get('following_count','')
    follower_count = html.get('follower_count','')
    answer_count = html.get('answer_count','')
    articles_count = html.get('articles_count','')
    temp.append(name)
    temp.append(gender)
    temp.append(education)
    temp.append(major)
    temp.append(company)
    temp.append(job)
    temp.append(location)
    temp.append(description)
    temp.append(headline)
    temp.append(following_count)
    temp.append(follower_count)
    temp.append(answer_count)
    temp.append(articles_count)
    return temp


def url_from_sql(id_number):
    print('url_from_sql')
    global db,cursor
    url_token = ' '
    sql = "SELECT * from user_list WHERE id=%s" % id_number
    try:
        cursor.execute(sql)
        res = cursor.fetchone()
        url_token = res[2]
        db.commit()
    except:
        print('error fetch the url_token')
    url = r'https://www.zhihu.com/api/v4/members/' + url_token + r'?include=locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2' \
                                                                 r'Cvoteup_count%2Cthanked_Count%2Cfollower_count%2Cfollowing_count%2Ccover_url' \
                                                                 r'%2Cfollowing_topic_count%2Cfollowing_question_count%2Cfollowing_favlists_count' \
                                                                 r'%2Cfollowing_columns_count%2Cavatar_hue%2Canswer_count%2Carticles_count%2Cpins_count' \
                                                                 r'%2Cquestion_count%2Ccolumns_count%2Ccommercial_question_count%2Cfavorite_count' \
                                                                 r'%2Cfavorited_count%2Clogs_count%2Cmarked_answers_count%2Cmarked_answers_text' \
                                                                 r'%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_bind_phone%2Cis_force_renamed' \
                                                                 r'%2Cis_bind_sina%2Cis_privacy_protected%2Csina_weibo_url%2Csina_weibo_name' \
                                                                 r'%2Cshow_sina_weibo%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed' \
                                                                 r'%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count' \
                                                                 r'%2Cthank_from_count%2Cthanked_count%2Cdescription%2Chosted_live_count' \
                                                                 r'%2Cparticipated_live_count%2Callow_message%2Cindustry_category%2Corg_name' \
                                                                 r'%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    return url


def url_switch():
    file_name = 'user_data.csv'
    url_token = ' '
    with open(file_name, 'r', errors='ignore', newline='')as f:
        f_csv = csv.DictReader(f)
        global number
        i=0
        for row in f_csv:
            i =i+1
            if i == number:
                url_token = row['url_token']
                number += 1
                break
    url = r'https://www.zhihu.com/api/v4/members/'+url_token+r'?include=locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2' \
                                                             r'Cvoteup_count%2Cthanked_Count%2Cfollower_count%2Cfollowing_count%2Ccover_url' \
                                                             r'%2Cfollowing_topic_count%2Cfollowing_question_count%2Cfollowing_favlists_count' \
                                                             r'%2Cfollowing_columns_count%2Cavatar_hue%2Canswer_count%2Carticles_count%2Cpins_count' \
                                                             r'%2Cquestion_count%2Ccolumns_count%2Ccommercial_question_count%2Cfavorite_count' \
                                                             r'%2Cfavorited_count%2Clogs_count%2Cmarked_answers_count%2Cmarked_answers_text' \
                                                             r'%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_bind_phone%2Cis_force_renamed' \
                                                             r'%2Cis_bind_sina%2Cis_privacy_protected%2Csina_weibo_url%2Csina_weibo_name' \
                                                             r'%2Cshow_sina_weibo%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed' \
                                                             r'%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count' \
                                                             r'%2Cthank_from_count%2Cthanked_count%2Cdescription%2Chosted_live_count' \
                                                             r'%2Cparticipated_live_count%2Callow_message%2Cindustry_category%2Corg_name' \
                                                             r'%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    return url


def write_data_file(item_data):
    file_name = 'user_info.csv'
    # with的使用保证了在处理文件过程中无论是否发生异常，都能保证关闭
    with open(file_name,'a',errors='ignore',newline='')as f:
        fieldnames = ['name','gender', 'education','major',
                      'company','job','location','description', 'headline','following_count','follower_count',
                      'answer_count','articles_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        global number
        if number is 1:
            writer.writeheader()
        writer.writerow({'name':item_data[0], 'gender':item_data[1],  'education':item_data[2],  'major':item_data[3],
                         'company':item_data[4], 'job':item_data[5],  'location':item_data[6],  'description':item_data[7],'headline': item_data[8],
                         'following_count': item_data[9], 'follower_count': item_data[10], 'answer_count': item_data[11], 'articles_count': item_data[12],})


def write_data_sql(item_data):
    global cursor
    global db
    try:
        sql = "INSERT IGNORE INTO user_info(name,gender,education,major,company,job,location,description," \
              "headline,following_count,follower_count,answer_count,articles_count) VALUES('%s',%s,'%s'," \
              "'%s','%s','%s','%s','%s','%s',%s,%s,%s,%s)" % (item_data[0], item_data[1], item_data[2],item_data[3],
               item_data[4], item_data[5],item_data[6],item_data[7],item_data[8],item_data[9],item_data[10],item_data[11],item_data[12])
        cursor.execute(sql)
        db.commit()
    except:
        print('write data is fail')
        db.rollback()
        write_data_file(item_data)


if __name__ == '__main__':
    while True:
        time.sleep(random.choice(range(5,20))/10.0)
        url = url_from_sql(id_number)
        id_number += 1
        html = get_content(url)
        if html is None:
            continue
        else:
            user_data = get_data_from_json(html)
        if user_data is None:
            continue
        else:
            print(user_data)
            write_data_sql(user_data)
