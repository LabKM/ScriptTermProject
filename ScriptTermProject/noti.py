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
import urllib

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
        if name_param == item.find("empNm").text:
            url = get_request_query(baseurl, 'getMemberDetailInfoList',
                                   {'numOfRows':'300', 'pageNo':'1', 'dept_cd': item.find("deptCd").text , 'num': item.find("num").text }, key)
            response = requests.get(url=url)
            detail_info = ET.fromstring(response.text).find('body').find('item')
            for info in detail_info:
                res_list.append((info.tag, info.text))
            break;
    return res_list

def getBookInfomation( name_param ):
    res_list = [] # list [ (저자, 제목, 내용, 출판사, 출판일, 이미지 파일경로), ... ]
    client_id = "0imDB_aqj8YSmssymgCT"
    client_secret = "z9JHpcE_yv"
    encText = urllib.parse.quote(name_param)
    encAuthour = urllib.parse.quote(name_param)
    url = "https://openapi.naver.com/v1/search/book_adv.xml?query=" + encText + "&display=3&sort=date&d_auth="+encAuthour # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    response_body = response.read()
    book_info_tree = ET.fromstring(response_body.decode('utf-8')).find('channel')
    for info in book_info_tree:
        if info.tag == "item":
            temp = (
                info.find("author").text, info.find("title").text, info.find("description").text, 
                info.find('publisher').text, info.find('pubdate').text, info.find('link').text,
                info.find("price").text, info.find('image').text
                )
            res_list.append( [t.replace("<b>", '').replace("</b>", '') for t in temp] )
    return res_list

def getAticleData( name_param ):
    client_id = "0imDB_aqj8YSmssymgCT"
    client_secret = "z9JHpcE_yv"
    encText = urllib.parse.quote(name_param + ' 국회의원')
    url = "https://openapi.naver.com/v1/search/news.xml?query=" + encText # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    response_body = response.read()
    book_info_tree = ET.fromstring(response_body.decode('utf-8')).find('channel')
    res_list = [] # list [ (제목, 내용, 기사 일자, 링크), ... ]
    for info in book_info_tree:
        if info.tag == "item":
            temp = (info.find("title").text, info.find("description").text, info.find("pubDate").text, info.find('link').text)
            res_list.append( [t.replace("<b>", '').replace("</b>", '') for t in temp] )
    return res_list

def getBillData( name_param ):#return list[ (의안 번호, 의안명, 처리 구분, 심사 진행 상태, 의안 발의 날짜, 발의 의원, 의안 결과(옵션), 주요내용(옵션)) ]
    url = get_request_query('http://apis.data.go.kr/9710000/BillInfoService2', 'getBillInfoList', 
                            {'numOfRows':'10', 'pageNo':'1', 'mem_name':name_param, 'ord':'21', 'start_ord':'21', 'end_ord':'21', 'gbn':'dae_num_name' }, 
                            'vcEXNHaIWXxS5Uz3hGYV%2FQKGjcxzIfqEvuV5Arl0yB66fMYdch6oxV1bMuTLSC7jXzr03Xzt1NkBrDBBzYIe2Q%3D%3D')
    res_body = requests.get(url=url)
    mem_tree = ET.fromstring(res_body.text).find("body").find("items")
    return mem_tree

def getPhotoUrl(name):
    for item in mem_tree:
        if name == item.find("empNm").text:
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
