import requests

cookies = {
    'Username': 'MjAyNTA2MTAyMDAwMDIxOQ%3D%3D',
    'Password': 'MDYwOTE2TGpq',
    'JSESSIONID': 'E0EA444AFA54FAF6C9D38A6665BE83A5',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Content-Length': '0',
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

params = {
    'term': '2026.1',
    'courseID': '1504110789',
}

response = requests.post(
    'https://xkxt2.ecjtu.edu.cn/TermPlan/TermPlan_getTeachTask.action',
    params=params,
    cookies=cookies,
    headers=headers,
)
print(response.text)

# ---------- 追加：保存为图片 ----------
from PIL import Image, ImageDraw, ImageFont
import os

def save_as_image(resp, filename="output.png"):
    try:
        data = resp.json()
    except Exception:
        print("响应不是JSON，跳过图片生成")
        return

    # 兼容直接列表或 {rows: [...]} 包装
    rows = data if isinstance(data, list) else data.get("rows", []) if isinstance(data, dict) else []
    if not rows:
        print("无数据，跳过图片生成")
        return

    # 加载字体
    font = None
    for p in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc"]:
        if os.path.exists(p):
            font = ImageFont.truetype(p, 16)
            break
    if not font:
        font = ImageFont.load_default()

    # 如需中文表头，按实际字段名修改下方字典
    RENAME = {}
    keys = list(rows[0].keys())
    headers = [RENAME.get(k, k) for k in keys]

    padding = 10
    row_h = 36
    header_h = 40

    def est_width(text):
        return len(str(text)) * 16 + padding * 2

    col_widths = []
    for i, k in enumerate(keys):
        w = max(est_width(headers[i]), est_width(k))
        for r in rows:
            w = max(w, est_width(r.get(k, "")))
        col_widths.append(w)

    total_w = sum(col_widths)
    total_h = header_h + row_h * len(rows)

    img = Image.new("RGB", (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 表头：绿底白字
    x = 0
    for i, h in enumerate(headers):
        draw.rectangle([x, 0, x + col_widths[i], header_h], fill=(0, 150, 136))
        draw.text((x + padding, 10), str(h), font=font, fill=(255, 255, 255))
        x += col_widths[i]

    # 数据行
    for ridx, row in enumerate(rows):
        y = header_h + ridx * row_h
        x = 0
        for i, k in enumerate(keys):
            draw.rectangle([x, y, x + col_widths[i], y + row_h], outline=(220, 220, 220))
            draw.text((x + padding, y + 8), str(row.get(k, "")), font=font, fill=(0, 0, 0))
            x += col_widths[i]

    # 边框
    draw.rectangle([0, 0, total_w - 1, total_h - 1], outline=(180, 180, 180))
    draw.line([(0, header_h), (total_w, header_h)], fill=(180, 180, 180), width=1)

    img.save(filename)
    print(f"已保存图片: {os.path.abspath(filename)}")


save_as_image(response)