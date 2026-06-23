import requests
import re
import html

#处理输出
def display_width(s):
    w = 0
    for ch in s:
        w += 2 if '一' <= ch <= '鿿' else 1
    return w
def pad(s, length, align='l'):
    w = display_width(s)
    pad_len = max(0, length - w)
    if align == 'r':
        return ' ' * pad_len + s
    return s + ' ' * pad_len
def strip_tags(text):
    return html.unescape(re.sub(r'<[^>]+>', '', text)).strip()
def print_course_table(html):
    rows_raw = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    data = []
    for row_html in rows_raw[1:]:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(tds) < 9:
            continue

        cells = [strip_tags(td) for td in tds[:7]]

        operate = strip_tags(tds[7])
        m = re.search(r'href="([^"]+)"', tds[7])
        if m:
            cells.append('选修')
        else:
            cells.append(operate)

        info_spans = re.findall(r'<span[^>]*>(.*?)</span>', tds[8], re.DOTALL)
        info = '\n'.join(strip_tags(s) for s in info_spans)
        cells.append(info)

        data.append(cells)

    headers_cn = ['学期', '课程', '课程要求', '考核方式', '学时', '学分', '选课类型', '选课操作', '选课信息']
    col_widths = [6, 24, 10, 8, 6, 6, 8, 8, 30]
    for i, h in enumerate(headers_cn):
        col_widths[i] = max(col_widths[i], display_width(h))
    for row in data:
        for i, cell in enumerate(row):
            lines = cell.split('\n')
            max_w = max(display_width(l) for l in lines) if lines else 0
            col_widths[i] = max(col_widths[i], max_w)

    def sep():
        parts = ['+' + '-' * (w + 2) for w in col_widths]
        print(''.join(parts) + '+')

    def print_row(cells):
        lines = [cell.split('\n') for cell in cells]
        max_lines = max(len(l) for l in lines)
        for r in range(max_lines):
            out = []
            for i in range(len(cells)):
                text = lines[i][r] if r < len(lines[i]) else ''
                out.append(' ' + pad(text, col_widths[i]) + ' ')
            print('|' + '|'.join(out) + '|')

    sep()
    print_row(headers_cn)
    sep()
    for row in data:
        if row[7] == '选修':
            print_row(row)
    sep()


cookies = {
    'Username': 'MjAyNTA2MTAyMDAwMDIxOQ%3D%3D',
    'Password': 'MDYwOTE2TGpq',
    'JSESSIONID': '0607F8822894257725B192025EE03C6B',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/xkNotice_getXKNoticeInfo.action?xkSelectType=1&eduType=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

response = requests.get(
    'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_getTeachTaskInfo.action',
    cookies=cookies,
    headers=headers,
)
print(response.text)
print_course_table(response.text)
