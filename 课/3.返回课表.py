import requests

cookies = {
    'Username': 'MjAyNTA2MTAyMDAwMDIxOQ%3D%3D',
    'Password': 'MDYwOTE2TGpq',
    'JSESSIONID': '33B10CE6C09919EF9D1110D7C0788B76',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'Username=MjAyNTA2MTAyMDAwMDIxOQ%3D%3D; Password=MDYwOTE2TGpq; JSESSIONID=33B10CE6C09919EF9D1110D7C0788B76',
}

response = requests.get(
    'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_getTeachTaskInfo.action',
    cookies=cookies,
    headers=headers,
)
print('状态码:', response.status_code)
print('URL:', response.url)
print(response.text)