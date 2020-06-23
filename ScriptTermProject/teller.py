#!/usr/bin/python
# coding=utf-8

import sys
import time
import sqlite3
import telepot
from pprint import pprint
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
import traceback

import noti

tagSet = {
    "empNm" : "의원이름", "hjNm" : "한자이름", "engNm": "영문이름", "bthDate": "생년월일",
    "polyNm" : "소속정당", "origNm" : "선거구", "shrtNm" : "소속위원회", "reeleGbnNm" : "당선횟수",
    "electionNum":"당선대수", "assemTel": "사무실전화", "assemHomep":"홈페이지", "assemEmail":"이메일",
    "staff":"보좌관", "secretary2":"비서관", "secretary":"비서", "hbbyCd":"취미", "examCd":"특기",
    "memTitle":"약력", 'deptCd': '부서코드', 'num': '식별코드', 'jpgLink': "의원 사진"
    }

def replyMemDataByLocation(user, param):
    print(user, param)
    res_list = noti.getDataByLocation( param )
    msg = ''
    cnt = 1
    for res in res_list:
        msg += str(cnt) + '. ' + res + '\n'
        cnt += 1
    if msg:
        noti.sendMessage(user, msg)
    else:
        noti.sendMessage(user, "해당 지역의 정보가 없습니다.")

def replyMemDataByName(user, param):
    print(user, param)
    res_list = noti.getDataByName( param )
    msg = ''
    cnt = 1
    for res in res_list:
        msg += str(cnt) + '. ' + res + '\n'
        cnt += 1
    if msg:
        noti.sendMessage(user, msg)
    else:
        noti.sendMessage(user, "해당 이름의 정보가 없습니다.")

def replyMemDataDetail(user, param_index):
    print(user, param_index)
    res_list = noti.getDataDetail(param_index) # Data Form list[ (tag, text) ]  text and tag are string
    msg = '' 
    photoUrl = noti.getPhotoUrl(param_index)
    if len(res_list) > 1 and photoUrl is not None:
        noti.sendPhoto(user, photoUrl)
    for res in res_list:
        if res[0] != "memTitle":
            msg += tagSet[res[0]] + ': ' + res[1] + '\n'
    if msg:
        noti.sendMessage(user, msg)
    else:
        noti.sendMessage(user, "잘못된 검색 키워드입니다.")

def replyMemTitle(user, param_name):
    print(user, param_name)
    res_list = noti.getDataDetail(param_name)
    msg = ''
    last_msg = '약력 없음'
    for res in res_list:
        if res[0] == "empNm" or res[0] == "bthDate" or res[0] == "bthDate" or\
           res[0] == "polyNm" or res[0] == "origNm" or res[0] == "shrtNm" or\
           res[0] == "hbbyCd" or res[0] == "examCd":
            msg += tagSet[res[0]] + ': ' + res[1] + '\n'
        elif res[0] == "memTitle":
            last_msg = '-약력-\n' + res[1] + '\n'
    msg += last_msg
    if msg:
        noti.sendMessage(user, msg)
    else:
        noti.sendMessage(user, "잘못된 검색 키워드입니다.")

def replyMemBook(user, param_name):
    print(user, param_name)
    res_list = noti.getBookInfomation(param_name)
    if len(res_list) > 0:
        for book in res_list:
            msg = ''
            noti.sendPhoto(book[-1])
            for i in range(len(book) - 1):
                msg += book[i] + '\n'
            if msg:
                noti.sendMessage(user, msg)
    else:
        noti.sendMessage(user, '저서가 없거나 해당 잘못된 국회의원 이름입니다.')

def save( user, loc_param ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    try:
        cursor.execute('INSERT INTO users(user, location) VALUES ("%s", "%s")' % (user, loc_param))
    except sqlite3.IntegrityError:
        noti.sendMessage( user, '이미 해당 정보가 저장되어 있습니다.' )
        return
    else:
        noti.sendMessage( user, '저장되었습니다.' )
        conn.commit()

def check( user ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    cursor.execute('SELECT * from users WHERE user="%s"' % user)
    for data in cursor.fetchall():
        row = 'id:' + str(data[0]) + ', location:' + data[1]
        noti.sendMessage( user, row )


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        noti.sendMessage(chat_id, '난 텍스트 이외의 메시지는 처리하지 못해요.')
        return

    text = msg['text']
    args = text.split(' ')

    if text.startswith('지역') and len(args)>1:
        print('try to 지역', args[1])
        replyMemDataByLocation( chat_id, args[1] )
    elif text.startswith('이름') and len(args)>1:
        print('try to 이름', args[1])
        replyMemDataByName( chat_id, args[1] )
    elif text.startswith('보기') and len(args)>1:
        print('try to 보기', args[1])
        replyMemDataDetail( chat_id, args[1] )
    elif text.startswith('약력') and len(args) > 1:
        print("try to 약력")
        replyMemTitle( chat_id, args[1] )
    elif text.startswith("저서") and len(args) > 1:
        print("try to 저서")
        replyMemBook(chat_id, args[1])
    #elif text.startswith('저장')  and len(args)>1:
    #    print('try to 저장', args[1])
    #    save( chat_id, args[1] )
    #elif text.startswith('확인'):
    #    print('try to 확인')
    #    check( chat_id )
    else:
        noti.sendMessage(chat_id, '모르는 명령어입니다.\n \
         가능한 명령어 : 지역 [지역이름], 이름 [한글이름], 보기 [한글이름], 약력 [한글이름]...등')


today = date.today()
current_month = today.strftime('%Y%m')

print( '[',today,']received token :', noti.TOKEN )

bot = telepot.Bot(noti.TOKEN)
pprint( bot.getMe() )

bot.message_loop(handle)

print('Listening...')

while 1:
  time.sleep(10)