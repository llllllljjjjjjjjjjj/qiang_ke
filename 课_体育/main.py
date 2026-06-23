import requests
import os
import json
import sys

# Windows 终端强制使用 UTF-8 输出，避免中文乱码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ==================== 每学期需要修改的配置 ====================
# 学期（例如: 2026.1 表示 2026 学年第一学期，2025.2 表示 2025 学年第二学期）
TERM = '2026.1'

# 体育课程 ID（不同学期可能需要修改，如 体育Ⅰ/Ⅱ/Ⅲ/Ⅳ 对应的 courseID 不同）
COURSE_ID = '1505100033'

# Cookie：JSESSIONID（Cookie 过期后需要重新登录获取并替换此处）
JSESSIONID = '6756949F751D760D8C81BDC3517E089A'
# ===========================================================

# 公共配置
cookies = {
    'JSESSIONID': JSESSIONID,
}

REQUEST_TIMEOUT = 15  # 请求超时时间（秒）

# 1. 获取课程列表的 headers
headers_get_tasks = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
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
}

# 2. 获取男女人数的 headers
headers_get_number = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
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
}

# 3. 提交选课的 headers
headers_select = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
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
}


def _check_cookie_expired(response):
    """检查响应是否为 HTML 登录页（Cookie 过期的典型表现）"""
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        return True
    # 有些系统过期后仍返回 200 但内容是登录页，通过文本特征再判断
    text = response.text[:200].lower()
    if '<!doctype html>' in text or '<html' in text:
        return True
    return False


def _safe_json(response, action_name):
    """安全地解析 JSON，并在 Cookie 过期时给出明确提示"""
    try:
        # 先尝试解析 JSON；有些系统 Content-Type 标错但内容仍是 JSON
        return response.json()
    except json.JSONDecodeError:
        # JSON 解析失败，再判断是不是被重定向到了 HTML 登录页
        if _check_cookie_expired(response):
            print(f"\n[错误] {action_name} 失败：Cookie 已过期，请重新登录获取 JSESSIONID 并更新配置。")
        else:
            print(f"\n[错误] {action_name} 返回的数据不是有效的 JSON。")
            print(f"返回内容前 200 字：{response.text[:200]}")
        return None


def get_courses():
    """获取可选课程列表（对应 1.表.py）"""
    url = 'https://xkxt2.ecjtu.edu.cn/Sports/Sports_getTeachTask.action'
    params = {
        'term': TERM,
        'courseID': COURSE_ID,
    }
    try:
        response = requests.post(
            url, params=params, cookies=cookies,
            headers=headers_get_tasks, timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        print(f"\n[错误] 获取课程列表超时（{REQUEST_TIMEOUT} 秒），请检查网络连接。")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n[错误] 网络连接失败，无法连接到教务系统：{e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n[错误] 获取课程列表请求异常：{e}")
        return None

    if response.status_code != 200:
        print(f"\n[错误] 获取课程列表失败，HTTP 状态码：{response.status_code}")
        return None

    data = _safe_json(response, "获取课程列表")
    if data is None:
        return None

    if not isinstance(data, list):
        print(f"\n[错误] 获取课程列表返回的数据格式异常，期望为列表，实际为：{type(data).__name__}")
        return None

    if len(data) == 0:
        print("\n[提示] 当前学期没有可选课程，请检查 TERM 和 COURSE_ID 配置是否正确。")
        return None

    return data


def get_numbers(teach_task_ids):
    """获取各课程的男女人数（对应 2.表的男女人数.py）"""
    if not teach_task_ids:
        return []

    url = 'https://xkxt2.ecjtu.edu.cn/Sports/Sports_getNumber.action'
    data = 'teachTasks=' + ','.join(teach_task_ids)
    try:
        response = requests.post(
            url, cookies=cookies, headers=headers_get_number,
            data=data, timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        print(f"\n[错误] 获取男女人数超时（{REQUEST_TIMEOUT} 秒），请检查网络连接。")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n[错误] 网络连接失败，无法获取男女人数：{e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n[错误] 获取男女人数请求异常：{e}")
        return None

    if response.status_code != 200:
        print(f"\n[错误] 获取男女人数失败，HTTP 状态码：{response.status_code}")
        return None

    data = _safe_json(response, "获取男女人数")
    if data is None:
        return None

    if not isinstance(data, list):
        print(f"\n[错误] 获取男女人数返回的数据格式异常，期望为列表，实际为：{type(data).__name__}")
        return None

    return data


def submit_course(course_info):
    """提交选课（对应 3.最后确认.py）"""
    # 字段安全检查
    required_fields = ['term', 'classTimeList', 'teachTaskID', 'courseID', 'creditHour']
    missing = [f for f in required_fields if f not in course_info]
    if missing:
        print(f"\n[错误] 课程信息缺少必要字段：{', '.join(missing)}，无法提交。")
        return None

    url = 'https://xkxt2.ecjtu.edu.cn/Sports/Sports_selectCourse.action'
    data = {
        'term': course_info['term'],
        'classTimeList': course_info['classTimeList'],
        'teachTaskID': course_info['teachTaskID'],
        'courseID': course_info['courseID'],
        'creditHour': str(course_info['creditHour']),
    }
    try:
        response = requests.post(
            url, cookies=cookies, headers=headers_select,
            data=data, timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        print(f"\n[错误] 提交选课超时（{REQUEST_TIMEOUT} 秒），请检查网络连接。")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n[错误] 网络连接失败，无法提交选课：{e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n[错误] 提交选课请求异常：{e}")
        return None

    if response.status_code != 200:
        print(f"\n[错误] 提交选课失败，HTTP 状态码：{response.status_code}")
        return None

    return _safe_json(response, "提交选课")


def main():
    # 1. 获取课程列表
    courses = get_courses()
    if courses is None:
        sys.exit(1)

    # 输出课程名称
    print("可选课程名称：")
    for i, c in enumerate(courses, start=1):
        name = c.get('teachClassCaption', '（未知课程名）')
        print(f"  {i}. {name}")

    # 2. 获取男女人数
    teach_task_ids = [c.get('teachTaskID') for c in courses if c.get('teachTaskID')]
    numbers = get_numbers(teach_task_ids)
    if numbers is None:
        sys.exit(1)

    # 建立 teachTaskID -> 人数信息的映射
    num_map = {n.get('teachTaskID'): n for n in numbers if n.get('teachTaskID')}

    # 输出课程名称、已选人数及剩余可选人数
    print("\n课程名称及人数：")
    for i, c in enumerate(courses, start=1):
        name = c.get('teachClassCaption', '（未知课程名）')
        teach_task_id = c.get('teachTaskID')
        num_info = num_map.get(teach_task_id, {})
        caption = num_info.get('selStuNumCaption', '未知')
        max_num = c.get('maxStuNum')
        sel_num = c.get('selStuNum')
        if isinstance(max_num, int) and isinstance(sel_num, int):
            remain = max_num - sel_num
        else:
            remain = '未知'
        print(f"  {i}. {name}  |  已选: {caption}  |  剩余可选: {remain}/{max_num if max_num is not None else '?'}")

    # 3. 让用户选择课程
    print("\n提示：输入课程序号进行选择，输入 q 可退出程序。")
    while True:
        try:
            choice = input("请输入要选择的课程序号: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n程序已取消。")
            sys.exit(0)

        if choice.lower() == 'q':
            print("程序已退出。")
            sys.exit(0)

        if not choice.isdigit():
            print("输入无效，请输入数字序号或 q 退出。")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(courses):
            print(f"输入无效，请输入 1-{len(courses)} 之间的数字。")
            continue

        selected = courses[idx]
        break

    name = selected.get('teachClassCaption', '（未知课程名）')
    print(f"\n您选择的课程是: {name}")
    print("正在提交选课请求...")

    # 4. 提交选课
    result = submit_course(selected)
    if result is None:
        sys.exit(1)

    print("\n提交结果：")
    print(json.dumps(result, ensure_ascii=False, indent=4))

    # 保存结果到文件
    try:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"\n结果已保存到: {output_path}")
    except OSError as e:
        print(f"\n[警告] 结果保存到文件失败：{e}")


if __name__ == '__main__':
    main()
