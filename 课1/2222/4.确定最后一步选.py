import requests
#准备好teachTaskID
cookies = {
    'Username': 'MjAyNTA2MTAyMDAwMDIxOQ%3D%3D',
    'Password': 'MDYwOTE2TGpq',
    'JSESSIONID': 'E0EA444AFA54FAF6C9D38A6665BE83A5',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_getTeachTaskInfo.action',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'Username=MjAyNTA2MTAyMDAwMDIxOQ%3D%3D; Password=MDYwOTE2TGpq; JSESSIONID=33B10CE6C09919EF9D1110D7C0788B76',
}

data = {
    'term': '2026.1',
    'classTimeList': '',
    'teachTaskID': '20261150411078900002',
    'courseID': '1504110789',
    'creditHour': '3.5',
}

response = requests.post(
    'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_selectCourse.action',
    cookies=cookies,
    headers=headers,
    data=data,
)
print(response.text)