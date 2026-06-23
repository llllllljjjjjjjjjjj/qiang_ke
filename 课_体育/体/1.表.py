import requests
import os
import json

#学期--课程id
cookies = {
    'JSESSIONID': '84CAF383B2493D4E4E62E414C9E3FFD4',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Content-Length': '0',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/Sports/Sports_getTeachTaskInfo.action',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'JSESSIONID=84CAF383B2493D4E4E62E414C9E3FFD4',
}

params = {
    'term': '2026.1',
    'courseID': '1505100033',
}

response = requests.post(
    'https://xkxt2.ecjtu.edu.cn/Sports/Sports_getTeachTask.action',
    params=params,
    cookies=cookies,
    headers=headers,
)
# 解析 JSON 并以好看格式输出到同目录文件
data = response.json()
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output表.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"已保存到: {output_path}")

