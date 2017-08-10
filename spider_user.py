import requests
import csv
import random
import time
import socket
import http.client
import pymysql

try:
    import cookielib
except:
    import http.cookiejar as cookielib

#数据库初始化连接
db = pymysql.connect('localhost','你的用户名','你的密码','zhihu',use_unicode=True, charset="utf8")
cursor = db.cursor()

#构建request请求的headers
#其中x-udid和authorization需要你通过浏览器自己查询，访问下面给出的例子即可
#https://www.zhihu.com/api/v4/members/excited-vczh/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment
# %2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit
# %2Ccomment_count%2Ccan_comment%2Ccontent%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time
# %2Cupdated_time%2Creview_info%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees
# %3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=20&limit=20&sort_by=created
agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.8',
    "Host": "www.zhihu.com",
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': agent,
    'Connection': 'keep-alive',
    'x-udid':'你的 x-udid',
    'Referer':'https://www.zhihu.com/people/excited-vczh/following',
    'authorization':'你的 authorization'
}

number = 0

# 功能：   通过get方法获取知乎用户列表
# 参数：   访问地址
# 返回值： 用户信息，当用户信息访问失败时，返回空
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

# 功能：   解析JSON信息，并以列表的形式返回
# 参数：   JSON格式的用户列表
# 返回值： 列表形式的用户列表
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
        # 通过限制follower_count的大小可以，将一些僵尸用户排除
        if follower_count >10000:
            final.append(temp)
    return final


# 功能：    从csv文件中选取下一个需要查找用户信息的用户
# 参数：    空
# 返回值：  用户的url地址
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


# 功能：   从数据库中选取下一个需要查询的用户
# 参数：   用户位置
# 返回值： 用户url地址
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

# 功能：   判断当前用户关注人是否已读取完毕，未读取完毕则继续读取，读取完毕则从数据库中查询下一用户的关注人列表
# 参数：   本用户关注的人JSON信息
# 返回值：  下一访问url
def url_switch(response):
    html = response.json()
    paging = html['paging']
    if paging['is_end'] is True:
        url = url_from_sql()
    else:
        url = paging['next']
    return url

# 功能：    将用户列表写入数据库中
# 参数：    列表形式的用户列表
# 返回值：  空
def write_data(data):
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

# 功能：   通过查询某一用户关注的人列表，保存所有被关注人，再逐一查询被关注人的关注人列表实现爬取大量知乎用户
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
            write_data(user_data)

