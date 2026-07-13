import requests

cookies = {
    'JSESSIONID': '4C016C1D25DB7F974290DA2742DBED37',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/common/common_selectedCourse.action',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'JSESSIONID=4C016C1D25DB7F974290DA2742DBED37',
}

data = {
    'term': '2026.1',
    'teachTaskID': '20261150011114000001',
    'courseID': '1500111140',
    'classTime': '130000000011001111111101111111100000000',
}

response = requests.post(
    'https://xkxt2.ecjtu.edu.cn/common/common_retreatCourses.action',
    cookies=cookies,
    headers=headers,
    data=data,
)
