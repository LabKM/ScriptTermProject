#2020 1학기 스크립트 강의 텀프로젝트 
#우리동네 국회의원 :  우동국

#기능 
# 1. 지역구 입력으로 국회의원 정보 가져오기
# 2. 국회의원의 최근 활동 보기
# 3. 국회의원 사무실 각종 정보 보기 
# 4. 의안 알아보기
# 5. 저서 확인하기
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from tkinter import messagebox
import urllib
import requests
import xml.etree.ElementTree as ET
from PIL import ImageTk, Image
from io import BytesIO
import webbrowser
import noti

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
        self.frames = []
        
        # 요청 URL과 오퍼레이션
        OPERATION = 'getMemberCurrStateList'
        PARAMS = {'numOfRows':'300', 'pageNo':'1'}

        request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
        response = requests.get(url=request_query)

        self.member_tree = ET.fromstring(response.text).find("body").find("items")
        self.fontstyle_name = font.Font(self.window, size=10, weight='bold', family='Consolas')
        self.fontstyle_info = font.Font(self.window, size=16, weight='bold', family='Consolas')
        self.fontstyle_detail_info = font.Font(self.window, size=9, weight='bold', family='Consolas')
        self.fontstyle_button = font.Font(self.window, size=12, weight='bold', family='Consolas')

        self.now_frame = 0
        self.set_frame_search()
        self.set_frame_show_info()

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
        self._0_textbox.grid(row=1,column=0) 
        self._0_textbox_result = tk.Button(self.frames[-1], text="검색", command=self.search_member_show_list)
        self._0_textbox_result.grid(row=1,column=1) 
        self._0_listbox = tk.Listbox(self.frames[-1], width=50, height=40)
        self._0_listbox.grid(row=2,column=0) 
        self._0_detail_button = tk.Button(self.frames[-1], text="자세히", command=self.show_detail_member)
        self._0_detail_button.grid(row=3, column=0)
        self.now_member = None
        self.frames[-1].grid_remove()

    def set_frame_show_info(self):
        self.frames.append(tk.Frame(self.window))
        self.frames[-1].grid(row=1, column=0)
        tk.Button(self.frames[-1],text="다른 국회 의원 검색",command=lambda X=0: self.frame_change(X)).grid(row=0, column=0)
        frame_photo = tk.Frame(self.frames[-1])
        frame_photo.grid(row=1, column=0)
        self.face_photo = tk.Label(frame_photo)
        self.face_photo.grid(row=1, column=0)
        self.name_label = tk.Label(frame_photo, font = self.fontstyle_name)
        self.name_label.grid(row=2, column=0)
        self.info_label= tk.Label(frame_photo, font = self.fontstyle_info)
        self.info_label.grid(row=1, column=1)

        frame_note = tk.Frame(self.frames[-1])
        frame_note.grid(row=2, column=0)
        self.notebook=ttk.Notebook(frame_note, width=800, height=600)
        self.notebook.grid(row=0, column=0)     

        frame_memtitle = tk.Frame(self.frames[-1])
        self.notebook.add(frame_memtitle, text="약력")
        self.TmemTitle = tk.Text(frame_memtitle, font=self.fontstyle_detail_info)
        self.TmemTitle.grid(row=0, column=1) 
        self.TmemTitle['state'] = 'disabled'

        self.set_frame_book_search()
        self.set_frame_aticle()
        self.set_frame_bill()

        self.button_homepage = tk.Button(frame_note, text="홈페이지 가보기", font=self.fontstyle_button, command=self.go_homepage)
        self.button_homepage.grid(row=1, column=0)
        self.frames[-1].grid_remove()

    def set_frame_book_search(self):
        frame_membook = tk.Frame(self.frames[-1])
        self.notebook.add(frame_membook, text="집필 서적")
        self.TmemBook = tk.Text(frame_membook,font=self.fontstyle_detail_info)
        self.TmemBook.grid(row=1, column=0)
        self.TmemTitle['state'] = 'disabled'

    def set_frame_aticle(self):
        frame_aticle = tk.Frame(self.frames[-1])
        self.notebook.add(frame_aticle, text='최근 기사')
        self.TmemAticle = tk.Text(frame_aticle,font=self.fontstyle_detail_info)
        self.TmemAticle.grid(row=0, column=0)
        self.TmemAticle['state'] = 'disabled'

    def set_frame_bill(self):
        frame_bill = tk.Frame(self.frames[-1])
        self.notebook.add(frame_bill, text='관련 의안')
        self.TmemBill = tk.Text(frame_bill,font=self.fontstyle_detail_info)
        self.TmemBill.grid(row=0, column=0)
        self.TmemBill['state'] = 'disabled'

    def frame_change(self, i):
        self.frames[self.now_frame].grid_remove()
        self.frames[i].grid()
        self.now_frame = i
        self.frames[self.now_frame].tkraise()

    def get_now_member(self):
        select = self._0_listbox.curselection()
        info = self._0_listbox.get(select)
        for item in self.member_tree:
            origNm = item.find("origNm").text
            if origNm == info:
                return self.parse_detail(item)

    def show_detail_member(self):
        self.frame_change(1)
        select = self._0_listbox.curselection()
        if len(select) > 0:
            self.now_member = self.get_now_member()
            self.set_face_label()
            self.show_default_info()
            self.show_member_title()
            self.show_member_book()
            self.show_aticle()
            self.show_member_bill()
        else:
            self.frame_change(0)

    def show_aticle(self):
        res_list = noti.getAticleData(self.now_member.find("empNm").text) # list [ (제목, 내용, 기사 일자, 링크), ... ]
        self.TmemAticle['state'] = 'normal'
        msg = ''
        for aticle in res_list:
            msg += '제목 : ' + aticle[0] + '\n'
            msg += '시간 : ' + aticle[2] + '\n'
            msg += aticle[1] + '\n'
            msg += aticle[3] + '\n\n\n'
            self.TmemAticle.insert(tk.END, msg)
        self.TmemAticle['state'] = 'disabled'

    def show_default_info(self):
        detail_item = self.now_member
        self.name_label["text"] = detail_item.find("empNm").text + '\n(' + detail_item.find("engNm").text + ', ' + detail_item.find('hjNm').text + ')'
        info_text = ''
        for some in detail_item:
            if some.tag == "polyNm" or some.tag == "origNm" or some.tag == "reeleGbnNm" or  \
                some.tag == "electionNum" or some.tag == "shrtNm" or some.tag == "assemHomep" or \
                some.tag == "assemEmail" or some.tag == "assemTel":
                info_text += tagSet[some.tag] + ' ' + some.text + '\n'
        self.info_label['text'] = info_text

    def go_homepage(self):
        if(self.now_member.find("assemHomep") != None):
            webbrowser.open_new(self.now_member.find("assemHomep").text)
        else:
            messagebox.showinfo("No Homepage", "해당 국회의원은 홈페이지 정보가 존재하지 않습니다.")

    def show_member_title(self):
        res_list = noti.getDataDetail(self.now_member.find("empNm").text)
        msg = ''
        last_msg = '그 외 약력 없음'
        for res in res_list:
            if res[0] == "empNm" or res[0] == "bthDate" or res[0] == "bthDate" or\
               res[0] == "polyNm" or res[0] == "origNm" or res[0] == "shrtNm" or\
               res[0] == "hbbyCd" or res[0] == "examCd":
                msg += tagSet[res[0]] + ': ' + res[1] + '\n'
            elif res[0] == "memTitle":
                last_msg = '-약력-\n' + res[1] + '\n'
        msg += last_msg
        self.TmemTitle['state'] = "normal"
        self.TmemTitle.insert(tk.INSERT, msg)
        self.TmemTitle['state'] = "disabled"

    def show_member_book(self):
        self.TmemBook['state'] = 'normal'
        self.TmemBook.delete('1.0', tk.END)
        book_info_list = noti.getBookInfomation(self.now_member.find("empNm").text)
        for book in book_info_list:
            msg = ''
            self.TmemBook.insert(tk.END, '\n\n')
            r = urllib.request.urlopen(book[-1]).read()
            temp = Image.open(BytesIO(r))
            photo = ImageTk.PhotoImage(temp)
            self.TmemBook.image_create(tk.END, image = photo)
            for i in range(len(book) - 1):
                msg += book[i] + '\n'
            self.TmemBook.insert(tk.END, msg)     
        self.TmemBook['state'] = 'disabled'

    def show_member_bill(self):
        self.TmemBill['state'] = 'normal'
        self.TmemBill.delete('1.0', tk.END)
        bill_info_tree = noti.getBillData(self.now_member.find("empNm").text)
        for bill_info in bill_info_tree:
            msg = bill_info.find("billName").text
            msg += '의안 번호: ' + bill_info.find("billNo").text + '\n'
            msg += '의안 구분: ' + bill_info.find("passGubn").text + '\n'
            msg += '심사 진행 상태: ' + bill_info.find("procStageCd").text + '\n'
            msg += '발의일' + bill_info.find("proposeDt").text + '\n'
            if bill_info.find("summary") is not None:
                msg += bill_info.find("summary").text + '\n'
            self.TmemBill.insert(tk.END, msg)
        self.TmemBill['state'] = 'disabled'


    def search_member_show_list(self):
        self._0_listbox.delete(0, tk.END)
        cnt = 0
        location = self._0_textbox.get()
        for item in self.member_tree:
            origNm = item.find("origNm").text
            if location in origNm:
                self._0_listbox.insert(cnt, origNm)
                cnt+=1

    def set_face_label(self):
        url = noti.getPhotoUrl(self.now_member.find("empNm").text)
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

import teller
#root.mainloop()


