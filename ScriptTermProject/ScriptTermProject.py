#2020 1학기 스크립트 강의 텀프로젝트 
#우리동네 국회의원 :  우동국

#기능 
# 1. 지역구 입력으로 국회의원 정보 가져오기
# 2. 국회의원의 최근 활동 보기
# 3. 국회의원 사무실 위치 보기
# 4. 국회의원 사무실로 이메일 전송
# 5. 국회의원 자기 지역구 이외에도 자신이 원하는 국회의원들 관심 등록 기능

from tkinter import *
import urllib
import requests
import xml.etree.ElementTree as ET

def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query


class Member:
    def __init__(self, item):
        self.item = item


class MainApp():
    def __init__(self, root):
        self.window = root
        self.window.title("우리 동네 국회의원")
        self.frame0 = Frame(root)
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

        Button(self.frame0,text="Search",command=lambda X=0: self.pressed(X)).pack(side=LEFT)
        self.frames.append(Frame(self.window))
        self.frames[-1].grid(row=1, column=0)
        self._0_location_member = StringVar()
        self._0_textbox = Entry(self.frames[-1], textvariable=self._0_location_member)
        self._0_textbox.grid(row=0,column=0) 
        self._0_textbox = Button(self.frames[-1], text="검색", command=self.search_member_show_list)
        self._0_textbox.grid(row=0,column=1) 
        self._0_listbox = Listbox(self.frames[-1])
        self._0_listbox.grid(row=1,column=0) 

    def pressed(self, i):
        self.frames[i].tkraise()

    def show_member(self, name):
        pass

    def search_member_show_list(self):
        self._0_listbox.delete(0, END)
        cnt = 0
        for item in self.member_tree:
            origNm = item.find("origNm").text
            if self._0_location_member.get() in origNm:
                self._0_listbox.insert(cnt, origNm + ":" + item.find('empNm').text)
                cnt+=1
        

root = Tk()
MainApp(root)
root.mainloop()


