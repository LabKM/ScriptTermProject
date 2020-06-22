#!/usr/bin/python

import sys
import time
import sqlite3
import telepot
from pprint import pprint
import requests
import xml.etree.ElementTree as ET
import re
from datetime import date, datetime, timedelta
import traceback

key = 'vcEXNHaIWXxS5Uz3hGYV%2FQKGjcxzIfqEvuV5Arl0yB66fMYdch6oxV1bMuTLSC7jXzr03Xzt1NkBrDBBzYIe2Q%3D%3D'
TOKEN = '1243598590:AAEBbKIqMfkBsKdf7D8aLHqiDxfXHHH0YCI'
MAX_MSG_LENGTH = 300
baseurl = 'http://apis.data.go.kr/9710000/NationalAssemblyInfoService'
bot = telepot.Bot(TOKEN)

def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query

url = get_request_query(baseurl, 'getMemberCurrStateList', {'numOfRows':'300', 'pageNo':'1'}, key)
res_body = requests.get(url=url)
mem_tree = ET.fromstring(res_body.text).find("body").find("items")

def getDataByLocation( loc_param ):
    res_list = []
    for item in mem_tree:
        if loc_param in item.find("origNm").text:
            res_list.append(item.find("origNm").text + " : " + item.find("empNm").text)
    return res_list

def getDataByName( name_param ):
    res_list = []
    for item in mem_tree:
        if name_param in item.find("empNm").text:
            res_list.append(item.find("empNm").text + " : " + item.find("origNm").text)
    return res_list

def getDataDetail( name_param ):
    res_list = []
    for item in mem_tree:
        if name_param in item.find("empNm").text:
            url = get_request_query(baseurl, 'getMemberDetailInfoList',
                                   {'numOfRows':'300', 'pageNo':'1', 'dept_cd': item.find("deptCd").text , 'num': item.find("num").text }, key)
            response = requests.get(url=url)
            detail_info = ET.fromstring(response.text).find('body').find('item')
            for info in detail_info:
                res_list.append((info.tag, info.text))
            break;
    return res_list

def getPhotoUrl(name):
    for item in mem_tree:
        if name in item.find("empNm").text:
            return item.find("jpgLink").text
    return None

def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)

def sendPhoto(user, photo_url):
    try:
        bot.sendPhoto(user, photo_url)
    except:
        traceback.print_exc(file=sys.stdout)

def run(date_param, param={'numOfRows':'300', 'pageNo':'1'}):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn.commit()

    user_cursor = sqlite3.connect('users.db').cursor()
    user_cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    user_cursor.execute('SELECT * from users')

    for data in user_cursor.fetchall():
        user, param = data[0], data[1]
        print(user, date_param, param)
        res_list = getData( param, date_param )
        msg = ''
        for r in res_list:
            try:
                cursor.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")'%(user,r))
            except sqlite3.IntegrityError:
                # 이미 해당 데이터가 있다는 것을 의미합니다.
                pass
            else:
                print( str(datetime.now()).split('.')[0], r )
                if len(r+msg)+1>MAX_MSG_LENGTH:
                    sendMessage( user, msg )
                    msg = r+'\n'
                else:
                    msg += r+'\n'
        if msg:
            sendMessage( user, msg )
    conn.commit()

if __name__=='__main__':
    today = date.today()
    current_month = today.strftime('%Y%m')

    print( '[',today,']received token :', TOKEN )

    pprint( bot.getMe() )

    run(current_month)