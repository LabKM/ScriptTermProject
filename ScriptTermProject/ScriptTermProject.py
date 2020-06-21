#2020 1학기 스크립트 강의 텀프로젝트 
#우리동네 국회의원 :  우동국

#기능 
# 1. 지역구 입력으로 국회의원 정보 가져오기
# 2. 국회의원의 최근 활동 보기
# 3. 국회의원 사무실 각종 정보 보기 
# 4. 국회의원 사무실로 이메일 전송
# 5. 저서 확인하기

import tkinter as tk
from tkinter import font
from tkinter import messagebox
import urllib
import requests
import xml.etree.ElementTree as ET
from PIL import ImageTk, Image
from io import BytesIO
import webbrowser

def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query

def get_request_image(url, file_name):
    r = requests.get(url=url)
    return r.content

URL = 'http://apis.data.go.kr/9710000/NationalAssemblyInfoService'

# 파라미터
SERVICEKEY = 'vcEXNHaIWXxS5Uz3hGYV%2FQKGjcxzIfqEvuV5Arl0yB66fMYdch6oxV1bMuTLSC7jXzr03Xzt1NkBrDBBzYIe2Q%3D%3D'

#tag match
tagSet = {
    "empNm" : "의원이름", "hjNm" : "한자이름", "engNM": "영문이름", "bthDate": "생년월일",
    "polyNm" : "소속정당", "origNm" : "선거구", "shrtNm" : "소속위원회", "reeleGbnNm" : "당선횟수",
    "electionNum":"당선대수", "assemTel": "사무실전화", "assemHomep":"홈페이지", "assemEmail":"이메일",
    "staff":"보좌관", "secretary2":"비서관", "secretary":"비서", "hbbyCd":"취미", "examCd":"특기",
    "memTitle":"약력"
    }

class MainApp():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("우리 동네 국회의원")
        self.window.geometry("640x480")
        self.frame0 = tk.Frame(self.window)
        self.frame0.grid(row=0,column=0)
        self.frames = []
        
        # 요청 URL과 오퍼레이션
        OPERATION = 'getMemberCurrStateList'
        PARAMS = {'numOfRows':'300', 'pageNo':'1'}

        request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
        response = requests.get(url=request_query)

        self.member_tree = ET.fromstring(response.text).find("body").find("items")

        tk.Button(self.frame0,text="Home",command=lambda X=0: self.frame_change(X)).pack(side=tk.LEFT)

        self.fontstyle_name = font.Font(self.window, size=10, weight='bold', family='Consolas')
        self.fontstyle_info = font.Font(self.window, size=16, weight='bold', family='Consolas')
        self.fontstyle_button = font.Font(self.window, size=12, weight='bold', family='Consolas')

        self.now_frame = 0
        self.set_frame_search()
        self.set_frame_show_info()
        self.set_frame_aticle()
        self.set_frame_current_sesstion()

        self.frames[self.now_frame].grid()
        self.frames[self.now_frame].tkraise()

        self.window.mainloop()

    def set_frame_search(self):
        self.frames.append(tk.Frame(self.window))
        self.frames[-1].grid(row=1, column=0)
        self._0_textbox = tk.Entry(self.frames[-1])
        self._0_textbox.insert(0, "지역구를 입력하세요")
        self._0_textbox.bind("<Button-1>", lambda event: self._0_textbox.delete(0, tk.END)) 
        self._0_textbox.bind("<Return>", lambda event: self.search_member_show_list()) 
        self._0_textbox.grid(row=0,column=0) 
        self._0_textbox_result = tk.Button(self.frames[-1], text="검색", command=self.search_member_show_list)
        self._0_textbox_result.grid(row=0,column=1) 
        self._0_listbox = tk.Listbox(self.frames[-1])
        self._0_listbox.grid(row=1,column=0) 
        self._0_detail_button = tk.Button(self.frames[-1], text="자세히", command=self.show_detail_member)
        self._0_detail_button.grid(row=2, column=0)
        self.now_member = None
        self.frames[-1].grid_remove()

    def set_frame_show_info(self):
        self.frames.append(tk.Frame(self.window))
        self.frames[-1].grid(row=1, column=0)
        self.face_photo = tk.Label(self.frames[-1])
        self.face_photo.grid(row=1, column=2)
        self.name_label = tk.Label(self.frames[-1], font = self.fontstyle_name)
        self.name_label.grid(row=2, column=2)
        self.info_label= tk.Label(self.frames[-1], font = self.fontstyle_info)
        self.info_label.grid(row=1, column=3)
        self.button_current = tk.Button(self.frames[-1], text="최근 활동 보기", font=self.fontstyle_button, command=self.show_current_session)
        self.button_current.grid(row=3, column=2)
        self.button_homepage = tk.Button(self.frames[-1], text="홈페이지 가보기", font=self.fontstyle_button, command=self.go_homepage)
        self.button_homepage.grid(row=3, column=3)
        self.frames[-1].grid_remove()

    def set_frame_aticle(self):
        self.frames.append(tk.Frame(self.window))        
        self.face_photo_aticle = tk.Label(self.frames[-1])
        self.face_photo_aticle.grid(row=1, column=2)
        self.name_label_aticle = tk.Label(self.frames[-1], font = self.fontstyle_name)
        self.name_label_aticle.grid(row=2, column=2)
        self.aticle_page = 0
        self.aticle_labels = []
        self.button_back_info = tk.Button(self.frames[-1], text="의원 정보", font=self.fontstyle_button, command=lambda : self.frame_change(1))
        self.button_back_info.grid(row=4, column=2)
        self.frames[-1].grid_remove()

    def set_frame_current_sesstion(self):
        self.frames.append(tk.Frame(self.window))        
        self.frames[-1].grid(row=1,column=0)
        self.face_photo_sesstion = tk.Label(self.frames[-1])
        self.face_photo_sesstion.grid(row=1, column=2)
        self.name_label_sesstion = tk.Label(self.frames[-1], font = self.fontstyle_name)
        self.name_label_sesstion.grid(row=2, column=2)
        self.sesstion_page = 0
        self.sesstion_labels = []
        self.button_back_info = tk.Button(self.frames[-1], text="의원 정보", font=self.fontstyle_button, command=lambda : self.frame_change(1))
        self.button_back_info.grid(row=3, column=2)
        self.frames[-1].grid_remove()

    def frame_change(self, i):
        self.frames[self.now_frame].grid_remove()
        self.frames[i].grid()
        self.now_frame = i
        self.frames[self.now_frame].tkraise()

    def show_detail_member(self):
        self.frame_change(1)
        select = self._0_listbox.curselection()
        if len(select) > 0:
            info = self._0_listbox.get(select)
            for item in self.member_tree:
                origNm = item.find("origNm").text
                if origNm == info:
                    self.set_image_label(item.find("jpgLink").text)
                    detail_item =  self.parse_detail(item)
                    self.name_label["text"] = detail_item.find("empNm").text + '\n(' + detail_item.find("engNm").text + ', ' + detail_item.find('hjNm').text + ')'
                    info_text = ''
                    for some in detail_item:
                        if some.tag == "polyNm" or some.tag == "origNm" or some.tag == "reeleGbnNm" or  \
                            some.tag == "electionNum" or some.tag == "shrtNm" or some.tag == "assemHomep" or \
                            some.tag == "assemEmail" or some.tag == "assemTel":
                            info_text += tagSet[some.tag] + ' ' + some.text + '\n'
                    self.info_label['text'] = info_text
                    self.aticle_page = 1
                    self.now_member = detail_item
                    break

    def show_aticle(self):
        self.frame_change(2)
        self.face_photo_aticle.configure(image=self.face_photo['image'])
        self.face_photo_aticle.image = self.face_photo['image']
        self.name_label_aticle['text'] = self.name_label['text']
        OPERATION = 'getPressAticle'
        PARAMS = {'numOfRows':'10', 'pageNo': str(self.aticle_page), 'hg_nm': self.now_member.find("empNm").text }
        request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
        response = requests.get(url=request_query)
        aticles = ET.fromstring(response.text).find('body').find('items')
        for label in self.aticle_labels:
            label.destroy()
        for aticle in aticles:
            self.aticle_labels.append(tk.Label(self.frames[2], font = self.fontstyle_info, text=aticle.find("title").text))
            self.aticle_labels[-1].bind("<Button-1>", lambda : webbrowser.open_new(aticle.find("url").text))
            self.aticle_labels[-1].grid(row=3, column=2)

    def go_homepage(self):
        if(self.now_member.find("assemHomep") != None):
            webbrowser.open_new(self.now_member.find("assemHomep").text)
        else:
            messagebox.showinfo("No Homepage", "해당 국회의원은 홈페이지 정보가 존재하지 않습니다.")

    def show_current_session(self):
        self.frame_change(3)
        self.face_photo_sesstion.configure(image=self.face_photo['image'])
        self.face_photo_sesstion.image = self.face_photo['image']
        self.name_label_sesstion['text'] = self.name_label['text']

    def search_member_show_list(self):
        self._0_listbox.delete(0, tk.END)
        cnt = 0
        location = self._0_textbox.get()
        for item in self.member_tree:
            origNm = item.find("origNm").text
            if location in origNm:
                self._0_listbox.insert(cnt, origNm)
                cnt+=1

    def set_image_label(self, url):
        r = urllib.request.urlopen(url).read()
        temp = Image.open(BytesIO(r))
        photo = ImageTk.PhotoImage(temp)
        self.face_photo.configure(image=photo)
        self.face_photo.image = photo

    def parse_detail(self, item):
        OPERATION = 'getMemberDetailInfoList'
        PARAMS = {'numOfRows':'1', 'pageNo':'1', 'dept_cd': item.find("deptCd").text , 'num': item.find("num").text }
        request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
        response = requests.get(url=request_query)
        mdi_et = ET.fromstring(response.text).find('body').find('item')
        return mdi_et


#root = Tk()
some = MainApp()
#root.mainloop()


