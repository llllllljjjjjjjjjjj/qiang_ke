import requests
import re
import html
import sys
from urllib.parse import parse_qs, urlparse

cookies = {
    'Username': 'MjAyNTA2MTAyMDAwMDIxOQ%3D%3D',
    'Password': 'MDYwOTE2TGpq',
    'JSESSIONID': '6756949F751D760D8C81BDC3517E089A',
}


def strip_tags(text):
    return html.unescape(re.sub(r'<[^>]+>', '', text)).strip()


def is_login_page(text):
    """判断是否被踢回登录页（严格匹配，避免课程名误触）"""
    if not text:
        return True
    lowered = text.lower()
    # 只有出现非常明确的登录/超时提示，才直接判定
    if any(m in lowered for m in ['请重新登录', '登录超时', '会话超时', 'session timeout', '请登录']):
        return True
    # 必须同时存在用户名输入框 + 密码输入框，才认为是登录页
    has_user = re.search(r'<input[^>]*name=["\']?(username|j_username|user)["\']?', text, re.I) is not None
    has_pwd = re.search(r'<input[^>]*type=["\']?password["\']?', text, re.I) is not None
    return has_user and has_pwd


def safe_post(url, **kwargs):
    """统一 POST，精准捕获各类异常"""
    try:
        resp = requests.post(url, timeout=(10, 30), **kwargs)
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f'请求超时: {e}')
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f'网络连接错误: {e}')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'请求异常: {e}')

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f'HTTP {resp.status_code}: {e}')

    return resp


def safe_get(url, **kwargs):
    """统一 GET，精准捕获各类异常"""
    try:
        resp = requests.get(url, timeout=(10, 30), **kwargs)
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f'请求超时: {e}')
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f'网络连接错误: {e}')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'请求异常: {e}')

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f'HTTP {resp.status_code}: {e}')

    return resp


def choose_term(courses):
    """从课程列表中提取学期，让用户选择（只有一个学期时自动跳过）"""
    terms = sorted({c['term'] for c in courses})
    if not terms:
        print('[失败] 未从课程列表中解析到学期信息')
        return None
    if len(terms) == 1:
        print(f'当前学期: {terms[0]}')
        return terms[0]

    print('检测到多个学期：')
    for i, t in enumerate(terms, 1):
        print(f'{i}. {t}')
    raw = input('\n请选择学期序号: ').strip()
    if not raw.isdigit():
        print('请输入正整数序号')
        return None
    idx = int(raw) - 1
    if idx < 0 or idx >= len(terms):
        print('序号超出范围')
        return None
    return terms[idx]


def get_optional_courses():
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
    try:
        resp = safe_get(
            'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_getTeachTaskInfo.action',
            cookies=cookies,
            headers=headers,
        )
    except RuntimeError as e:
        print(f'[失败] 获取课程列表时出错: {e}')
        return None

    text = resp.text
    if is_login_page(text):
        print('[失败] 会话已失效，返回了登录页面，请更新 JSESSIONID。')
        print(f'[调试] 响应内容前300字符: {text[:300]}')
        return None

    rows_raw = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    if not rows_raw:
        print('[失败] 课程列表页未解析到任何表格行，页面结构可能已变更。')
        return None

    courses = []
    for row_html in rows_raw[1:]:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(tds) < 9:
            continue
        operate_html = tds[7]
        m = re.search(r'href="([^"]+)"', operate_html)
        if not m:
            continue
        href = m.group(1)
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)
        term = qs.get('term', [''])[0]
        course_id = qs.get('courseID', [''])[0]
        if not term or not course_id:
            continue
        cells = [strip_tags(td) for td in tds[:7]]
        courses.append({
            'term': term,
            'courseID': course_id,
            '学期': cells[0],
            '课程': cells[1],
            '课程要求': cells[2],
            '考核方式': cells[3],
            '学时': cells[4],
            '学分': cells[5],
            '选课类型': cells[6],
        })

    return courses


def get_teach_task(term, course_id):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
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
    }
    params = {
        'term': term,
        'courseID': course_id,
    }
    try:
        resp = safe_post(
            'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_getTeachTask.action',
            params=params,
            cookies=cookies,
            headers=headers,
        )
    except RuntimeError as e:
        print(f'[失败] 获取课程(task)信息时出错: {e}')
        return None

    text = resp.text
    if is_login_page(text):
        print('[失败] 会话已失效，返回了登录页面，请更新 JSESSIONID。')
        return None

    try:
        data = resp.json()
    except Exception as e:
        print(f'[失败] 解析课程(task)JSON失败: {e}')
        print(f'[调试] 原始响应前200字符: {text[:200]}')
        return None

    rows = data if isinstance(data, list) else data.get('rows', []) if isinstance(data, dict) else []
    if not rows:
        print('[失败] 课程(task)返回为空列表或无 rows 字段。')
        print(f'[调试] 解析后的数据: {data}')
        return None

    first = rows[0]
    if not isinstance(first, dict):
        print(f'[失败] 课程(task)首条记录不是字典: {type(first)}')
        return None

    if 'teachTaskID' not in first:
        print(f'[失败] 课程(task)记录缺少 teachTaskID 字段，可用字段: {list(first.keys())}')
        return None

    return first


def submit_course(term, course_id, credit_hour, task):
    teach_task_id = task.get('teachTaskID')
    class_time_list = task.get('classTimeList', '')
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
    }
    data = {
        'term': term,
        'classTimeList': class_time_list,
        'teachTaskID': teach_task_id,
        'courseID': course_id,
        'creditHour': credit_hour,
    }
    try:
        resp = safe_post(
            'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_selectCourse.action',
            cookies=cookies,
            headers=headers,
            data=data,
        )
    except RuntimeError as e:
        print(f'[失败] 提交选课时出错: {e}')
        return None

    text = resp.text
    if is_login_page(text):
        print('[失败] 会话已失效，返回了登录页面，请更新 JSESSIONID。')
        return None

    # 尝试解析 JSON，否则返回文本
    try:
        return resp.json()
    except Exception:
        return text


def main():
    try:
        courses = get_optional_courses()
    except Exception as e:
        print(f'[严重错误] 获取课程列表时发生未捕获异常: {e}')
        sys.exit(1)

    if courses is None:
        sys.exit(1)
    if not courses:
        print('暂无可选课程')
        sys.exit(0)

    term = choose_term(courses)
    if term is None:
        sys.exit(1)
    courses = [c for c in courses if c['term'] == term]
    if not courses:
        print('该学期暂无可选课程')
        sys.exit(0)

    print('可选课程列表：')
    for i, c in enumerate(courses, 1):
        print(f"{i}. {c['课程']} | {c['课程要求']} | {c['考核方式']} | 学分:{c['学分']} | 类型:{c['选课类型']}")

    raw = input('\n请输入要选择的课程序号: ').strip()
    if not raw.isdigit():
        print('请输入正整数序号')
        sys.exit(1)

    choice = int(raw) - 1
    if choice < 0 or choice >= len(courses):
        print('序号超出范围')
        sys.exit(1)

    course = courses[choice]
    print(f"\n正在获取课程 {course['课程']} 的信息...")
    task = get_teach_task(course['term'], course['courseID'])
    if not task:
        sys.exit(1)

    teach_task_id = task.get('teachTaskID')
    if not teach_task_id:
        print('[失败] 未获取到 teachTaskID')
        sys.exit(1)

    print(f"正在提交选课: {course['课程']} ...")
    result = submit_course(course['term'], course['courseID'], course['学分'], task)
    if result is None:
        sys.exit(1)

    print('提交结果:', result)


if __name__ == '__main__':
    main()
