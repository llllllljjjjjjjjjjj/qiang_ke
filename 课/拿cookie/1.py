import os, requests, execjs, random, time
from user import User
import ddddocr

SecretKey="F4&JF5*13$W7+C96C=6E4@1E9B#EAEA&4C1J#7A*FT2(B9U!C5)F0%3L^0C4B4"
headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '1.js'), 'r', encoding='utf-8') as f:
    js_code = f.read()
ctx = execjs.compile(js_code)
User1 = User()
session = requests.Session()
ocr = ddddocr.DdddOcr(show_ad=False)

#写入验证码
resp = session.get(f'https://xkxt2.ecjtu.edu.cn/servlet/code.servlet?rm={random.random()}', headers=headers)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code.png'), 'wb') as f:
    f.write(resp.content)
    
#获取验证码
code = ocr.classification(resp.content)
print('识别验证码:', code)

data = {
    'username': ctx.call('encryptByDES', User1.user_name, SecretKey),
    'password': ctx.call('encryptByDES', User1.user_pwd, SecretKey),
    'code': code,
}

response = session.post('https://xkxt2.ecjtu.edu.cn/login/login_checkout.action', headers=headers, data=data)
print('登录响应:', response.text)

# 登录成功后请求通知接口
notice_url = 'https://xkxt2.ecjtu.edu.cn/xkNotice_getXKNoticeInfo.action?xkSelectType=1&eduType=1'

t1 = time.time()
notice_resp = session.get(notice_url, headers=headers)
print(notice_resp.cookies)
# t2 = time.time()

# print(f'请求通知接口耗时: {t2 - t1:.2f} 秒')
# print('\n===== 通知接口详情 =====')
# print('状态码:', notice_resp.status_code)
# print('URL:', notice_resp.url)
# print('\n--- 响应头 ---')
# for k, v in notice_resp.headers.items():
#     print(f'{k}: {v}')
# print('\n--- 当前 Cookies ---')
# for c in session.cookies:
#     print(f'{c.name}={c.value} (domain={c.domain}, path={c.path})')
# print('\n--- 响应体 ---')
# print(notice_resp.text)
# print('===== 结束 =====')


#只有开放权限后才可以