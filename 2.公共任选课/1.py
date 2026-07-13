import requests

cookies = {
    'JSESSIONID': 'FF48C80766D0C86826A383FEECE57DA8',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Content-Length': '0',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getCoureTeachTask.action?currentPage=4',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'JSESSIONID=365FC6204488FD5ECF90E45FF905064A',
}

response = requests.post(
    'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getSelCourseNum.action?teachTaskIDs=20261150011121000001,20261150011120000001',
    cookies=cookies,
    headers=headers,
)
print(response.text)