#2020 1학기 스크립트 강의 텀프로젝트 
#우리동네 국회의원 :  우동국

#기능 
# 1. 지역구 입력으로 국회의원 정보 가져오기
# 2. 국회의원의 최근 활동 보기
# 3. 국회의원 사무실 위치 보기
# 4. 국회의원 사무실로 이메일 전송
# 5. 국회의원 자기 지역구 이외에도 자신이 원하는 국회의원들 관심 등록 기능

import urllib
import requests

def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query


# 요청 URL과 오퍼레이션
URL = 'http://apis.data.go.kr/9710000/NationalAssemblyInfoService'
OPERATION = 'getMemberCurrStateList' # 국경일 + 공휴일 정보 조회 오퍼레이션

# 파라미터
SERVICEKEY = 'vcEXNHaIWXxS5Uz3hGYV%2FQKGjcxzIfqEvuV5Arl0yB66fMYdch6oxV1bMuTLSC7jXzr03Xzt1NkBrDBBzYIe2Q%3D%3D'
PARAMS = {'numOfRows':'300', 'pageNo':'1'}

request_query = get_request_query(URL, OPERATION, PARAMS, SERVICEKEY)
response = requests.get(url=request_query)

orig = input("지역구 입력 : ")

import xml.etree.ElementTree as ET
root = ET.fromstring(response.text)

for item in root.iter('item'):
    if ( orig == item.find('origNm').text ):
        for str in item.iter():
            print(str.text)






#class Member:
#    def __init__(self, name):
#        self.name = name

#    def extractBookData(strXml): #strXml은 OpenAPI 검색 결과 XML 문자열
#        tree = ElementTree.fromstring(strXml)
#        print (strXml)
#        # Book 엘리먼트를 가져옵니다.
#        itemElements = tree.getiterator("item")    # item 엘리먼트 리스트 추출
#        print(itemElements)

#        for item in itemElements:
#            isbn = item.find("isbn")          #isbn 검색
#            strTitle = item.find("title")     #title 검색
#            print (strTitle)
#            if len(strTitle.text) > 0 :
#               return {"ISBN":isbn.text,"title":strTitle.text} # 사전형식 반환


#class MainApp():
#    def __init__(self, root):
#        self.window = root
#        self.window.title("우리 동네 국회의원")
#        self.frames = []
        
#        self.member_dict = dict()

#        self.frames.append(Frame(self.window))
#        self.frames[0].pack()
       
#        self.show_member_name = Label(self.frames[0].)
        

#    def insert_member(self, info):
#        self.member_dict[info] = Member(info)

#    def show_member(self, name):
#        pass
        
       
        

#root = Tk()
#MainApp(root)
#root.mainloop()


