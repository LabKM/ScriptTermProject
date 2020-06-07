#2020 1학기 스크립트 강의 텀프로젝트 
#우리동네 국회의원 :  우동국

#기능 
# 1. 지역구 입력으로 국회의원 정보 가져오기
# 2. 국회의원의 최근 활동 보기
# 3. 국회의원 사무실 위치 보기
# 4. 국회의원 사무실로 이메일 전송
# 5. 국회의원 자기 지역구 이외에도 자신이 원하는 국회의원들 관심 등록 기능

import tkinter as tk
import urllib
import requests
import xml.etree.ElementTree as ET
from PIL import ImageTk, Image
from io import BytesIO

def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query

def get_request_image(url, file_name):
    r = requests.get(url=url)
    return r.content

class Member:
    def __init__(self, item):
        self.item = item


class MainApp():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("우리 동네 국회의원")
        self.window.geometry("640x480")
        self.frame0 = tk.Frame(self.window)
        self.frame0.grid(row=0,column=0)
        self.frames = []
        
        # 요청 URL과 오퍼레이션
        URL = 'http://apis.data.go.kr/9710000/NationalAssemblyInfoService'
        OPERATION = 'getMemberCurrStateList' # 국경일 + 공휴일 정보 조회 오퍼레이션

        # 파라미터
        SERVICEKEY = 'vcEXNHaIWXxS5Uz3hGYV%2FQKGjcxzIfqEvuV5Arl0yB66fMYdch6oxV1bMuTLSC7jXzr03Xzt1NkBrDBBzYIe2Q%3D%3D'
        PARAMS = {'numOfRows':'300', 'pageNo':'1'}

        request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
        response = requests.get(url=request_query)

        self.member_tree = ET.fromstring(response.text).find("body").find("items")

        tk.Button(self.frame0,text="Home",command=lambda X=0: self.pressed(X)).pack(side=tk.LEFT)
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

        temp = Image.open("AsteroidSprite.png")
        photoimg = ImageTk.PhotoImage(temp)
        self.face_photo = tk.Label(self.frames[-1], image=photoimg)
        self.face_photo.grid(row=1, column=2)

        self.info_label= tk.Label(self.frames[-1])
        self.info_label.grid(row=2, column=2)

        self._0_detail_button = tk.Button(self.frames[-1], text="자세히", command=self.show_detail_member)
        self._0_detail_button.grid(row=2, column=0)

        self.window.mainloop()
    def pressed(self, i):
        self.frames[i].tkraise()

    def show_detail_member(self):
        select = self._0_listbox.curselection()
        if len(select) > 0:
            info = self._0_listbox.get(select)
            for item in self.member_tree:
                origNm = item.find("origNm").text
                if origNm == info:
                    self.set_image_label(item.find("jpgLink").text)
                    self.info_label['text'] = item.find("empNm").text + '(' + item.find("engNm").text + ')\n' + origNm \
                        + '\n' + item.find("reeleGbnNm").text


    def show_member(self):
        select = self._0_listbox.curselection()
        if len(select) > 0 and self.select != select[0]:
            info = self._0_listbox.get(select)
            for item in self.member_tree:
                origNm = item.find("origNm").text
                if origNm == info:
                    self.set_image_label(item.find("jpgLink").text)
                    break

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
        

#root = Tk()
some = MainApp()
#root.mainloop()


