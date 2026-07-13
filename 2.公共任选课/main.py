import requests
from bs4 import BeautifulSoup
import unicodedata
import json
import os

# 从外部文件读取 cookie，避免每次改代码
cookie_path = os.path.join(os.path.dirname(__file__), 'cookie.json')
if not os.path.exists(cookie_path):
    print('错误：找不到 cookie.json，请在同目录下创建并写入最新的 JSESSIONID。')
    print('格式示例：{"JSESSIONID": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}')
    exit(1)

try:
    with open(cookie_path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
except Exception as e:
    print(f'错误：读取 cookie.json 失败，{e}')
    exit(1)

if 'JSESSIONID' not in cookies:
    print('错误：cookie.json 里缺少 JSESSIONID 字段。')
    exit(1)

headers_html = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getCoureTeachTask.action',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

headers_selnum = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getCoureTeachTask.action',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

headers_select = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://xkxt2.ecjtu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getCoureTeachTask.action',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def _text_width(s):
    """计算字符串在终端中的显示宽度（中文算2，英文算1）"""
    w = 0
    for ch in str(s):
        if unicodedata.east_asian_width(ch) in ('F', 'W', 'A'):
            w += 2
        else:
            w += 1
    return w


def _pad(s, width):
    """将字符串补齐或截断到指定显示宽度"""
    s = str(s)
    w = _text_width(s)
    if w > width:
        result = ''
        cur = 0
        for ch in s:
            cw = 2 if unicodedata.east_asian_width(ch) in ('F', 'W', 'A') else 1
            if cur + cw > width - 1:
                result += '.'
                break
            result += ch
            cur += cw
        while _text_width(result) < width:
            result += ' '
        return result
    return s + ' ' * (width - w)


def _print_row(cols, widths):
    """打印一行表格内容，cols为字符串列表，widths为对应显示宽度"""
    parts = ['|']
    for col, w in zip(cols, widths):
        parts.append(' ' + _pad(col, w) + ' |')
    print(''.join(parts))


def _print_sep(widths):
    """打印表格分隔线"""
    parts = ['+']
    for w in widths:
        parts.append('-' * (w + 2) + '+')
    print(''.join(parts))


def fetch_courses(page=1):
    """获取指定页的课程列表，返回 (courses, total_pages)
    courses: 课程字典列表
    total_pages: 总页数（从HTML解析，若解析失败返回1）
    """
    params = {'currentPage': str(page)}
    resp = requests.get(
        'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getCoureTeachTask.action',
        params=params,
        cookies=cookies,
        headers=headers_html,
    )
    resp.encoding = resp.apparent_encoding or 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', id='course-data')
    if not table:
        # 按页保存调试信息，避免覆盖
        debug_file = f'debug_page_{page}.html'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(resp.text)
        return [], 1

    # 解析总页数
    total_pages = 1
    page_total_input = soup.find('input', id='pageTotal')
    if page_total_input and page_total_input.get('value'):
        try:
            total_pages = int(page_total_input['value'])
        except ValueError:
            total_pages = 1

    rows = table.find_all('tr')[1:]  # 跳过表头
    courses = []
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 12:
            continue

        term_input = row.select_one('.term')
        tea_input = row.select_one('.teaTaID')
        course_input = row.select_one('.courseID')
        time_input = row.select_one('.classTimeList')

        term = term_input['value'] if term_input else ''
        teach_task_id = tea_input['value'] if tea_input else ''
        course_id = course_input['value'] if course_input else ''
        class_time = time_input['value'] if time_input else ''

        # 课程名称在第3个 td（索引2）
        course_name = tds[2].get_text(strip=True)
        # 教师在第9个 td（索引8）
        teacher = tds[8].get_text(strip=True)
        # 容量在第10个 td（索引9）
        capacity = tds[9].get_text(strip=True)
        # 已选人数在第11个 td（索引10），初始为空，需要后续 AJAX 获取
        selected = tds[10].get_text(strip=True)

        # 判断是否已经选了：操作列是第12个 td（索引11）
        operate_td = tds[11]
        is_selected = '已选' in operate_td.get_text()

        courses.append({
            'term': term,
            'teachTaskID': teach_task_id,
            'courseID': course_id,
            'classTime': class_time,
            'name': course_name,
            'teacher': teacher,
            'capacity': capacity,
            'selected': selected,
            'is_selected': is_selected,
        })
    return courses, total_pages


def fetch_selected_numbers(courses):
    """通过 AJAX 获取已选人数并填充到 courses 中"""
    if not courses:
        return
    ids = ','.join([c['teachTaskID'] for c in courses if c['teachTaskID']])
    if not ids:
        return
    url = f'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_getSelCourseNum.action?teachTaskIDs={ids}'
    try:
        resp = requests.post(url, cookies=cookies, headers=headers_selnum)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        data = resp.json()
        # 用 teachTaskID 做映射，避免索引错位
        id_to_num = {}
        for item in data:
            tid = item.get('teachTaskID') or item.get('teachTaskId')
            if tid:
                id_to_num[str(tid)] = str(item.get('selStuNum', ''))
        for c in courses:
            if c['teachTaskID'] in id_to_num:
                c['selected'] = id_to_num[c['teachTaskID']]
    except Exception as e:
        print(f'[警告] 获取已选人数失败：{e}')


def select_course(course):
    """提交选课请求"""
    data = {
        'teachTaskInfo.term': course['term'],
        'teachTaskInfo.teachTaskID': course['teachTaskID'],
        'teachTaskInfo.courseID': course['courseID'],
        'classTime.classTime': course['classTime'],
    }
    try:
        resp = requests.post(
            'https://xkxt2.ecjtu.edu.cn/commonXK/commonXK_selectCourse.action',
            cookies=cookies,
            headers=headers_select,
            data=data,
        )
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text.strip()
    except Exception as e:
        return f'网络错误：{e}'


def main():
    print('正在获取第 1 页课程列表...')
    courses, total_pages = fetch_courses(page=1)
    if not courses:
        print('未获取到课程，请检查登录状态（JSESSIONID 是否过期）。')
        return

    fetch_selected_numbers(courses)
    all_courses = courses[:]

    # 自动获取剩余页数
    if total_pages > 1:
        for page in range(2, total_pages + 1):
            print(f'正在获取第 {page} 页课程列表...')
            courses, _ = fetch_courses(page=page)
            if courses:
                fetch_selected_numbers(courses)
                all_courses.extend(courses)

    print()
    col_widths = [4, 26, 10, 6, 8, 6]
    headers = ['序号', '课程名称', '教师', '容量', '已选人数', '状态']

    _print_sep(col_widths)
    _print_row(headers, col_widths)
    _print_sep(col_widths)
    for idx, c in enumerate(all_courses, start=1):
        status = '已选' if c['is_selected'] else '未选'
        _print_row([
            idx,
            c['name'],
            c['teacher'],
            c['capacity'],
            c['selected'] if c['selected'] else '-',
            status,
        ], col_widths)
    _print_sep(col_widths)
    print()
    choice = input('请输入要选择的课程序号（输入 0 取消）：').strip()
    if not choice.isdigit():
        print('输入无效，已取消。')
        return
    choice = int(choice)
    if choice == 0:
        print('已取消。')
        return
    if choice < 1 or choice > len(all_courses):
        print('序号超出范围，已取消。')
        return

    target = all_courses[choice - 1]
    if target['is_selected']:
        print('该课程已经选过了。')
        return

    print(f'正在提交选课：{target["name"]} ...')
    result = select_course(target)

    msg_map = {
        '1': '选课成功！',
        '0': '选课失败！',
        '-1': '选课人数已满！',
        '-2': '不在选课范围！',
        '-3': '上课时间发生冲突！',
        '-4': '发生异常，选课失败！',
        '-5': '对不起，你的公共任选课选课已满！',
    }
    print(msg_map.get(result, f'未知返回码：{result}'))


if __name__ == '__main__':
    main()
