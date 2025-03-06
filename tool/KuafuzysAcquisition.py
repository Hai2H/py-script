import re
from time import sleep
from urllib.parse import urlencode

import urllib3
from lxml import etree

import requests
from bs4 import BeautifulSoup

from database import BBSInfo

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = "https://www.kuafuzys.com/"

bbs_sid = "2mud9mujcg0fj8vraibelosfcs"
bbs_token = "_2BF4zHnTYdq1TohaEEkRRtKv4PegHYqvfTEohQ475omOG5SnZaOJqnKQ_2FCI9kip6o8P99YKD4rsx2NASbkU_2B_2BxPQ7t6x4I85Z"
cookie = f"bbs_sid={bbs_sid}; bbs_token={bbs_token}; "

quake_new = "{quake_new_url}"

# 获取列表
def get_bbs_list(uid, page):
    """
    获取列表
    :param uid: 用户ID
    :param page: 页数
    """
    print("夸父资源社>>> 获取列表 uid:{}, 页码:{} ", uid, page)
    url = base_url + f"user-thread-{uid}-{page}.htm"
    try:
        # 发送 GET
        response = requests.get(url)
        # 检查请求是否成功
        if response.status_code == 200:
            # 使用 BeautifulSoup 解析 HTML 内容
            soup = BeautifulSoup(response.text, 'html.parser')
            # 根据优化后的 CSS 选择器提取元素
            li_elements = soup.find_all('li', class_='media thread tap')
            results = []
            for li in li_elements:
                # 提取主题链接
                body = li.find('div', class_='media-body')
                thread_link = body.find('a',href=True)['href']
                # # 提取主题标题
                thread_title = body.find('a', href=True).get_text()
                bbs_info = BBSInfo(
                    uid=uid,
                    title=thread_title,
                    source="夸父资源社",
                    thread_link=base_url + thread_link,
                    code=extract_number_from_url(thread_link)
                )
                results.append(bbs_info)
            return results
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求出现异常: {e}")
# 获取详情
def get_detail(bbs_info):
    extracted_html = BeautifulSoup("", "html.parser")
    is_reply = True
    while is_reply:
        print(f"夸父资源社>>> 获取详情,标题:{bbs_info.title}")
        html_content = get_html_info(bbs_info.thread_link)
        # 创建解析器
        parser = etree.HTMLParser()
        tree = etree.HTML(html_content, parser)
        # 定义 整体内容 路径
        body_xpath_path = '/html/body/main/div/div/div[2]/div[1]/div[2]/div'
        # 使用 XPath 提取整体内容
        body = tree.xpath(body_xpath_path)[0]
        node_html = etree.tostring(body, encoding='unicode')
        # 复制提取出来的部分，以便后续操作
        extracted_html = BeautifulSoup(str(node_html), 'html.parser')
        # 栏目
        bbs_info.node = tree.xpath('/html/body/main/div/div/div[2]/div[1]/div[1]/div/div/div/div/div/div/div[1]/span[1]/a/text()')[0]
        # 标签
        tags_f = tree.xpath('/html/body/main/div/div/div[2]/div[1]/div[2]/div[2]/a/text()')
        if tags_f:
            bbs_info.tags = ','.join(tags_f)

        # 判断是否包含上面内容
        target_content = '您好，本帖含有特定内容，请'
        # 查找匹配的标签，find_all会返回所有匹配的结果列表，如果找到则列表不为空
        matching_tags = extracted_html.find_all('div', class_='alert alert-warning', role='alert')
        is_ok = False
        for tag in matching_tags:
            print(tag)
            if target_content in tag:
                print("夸父资源社>>>包含待回复的匹配块")
                print("夸父资源社>>>内容回复", bbs_info.title)
                send_comment(bbs_info.code)
                sleep(5)
                is_ok = True
                break
        if is_ok:
            continue
        else:
            is_reply = False
            print("夸父资源社>>> 已评论")
        # is_reply = False

    return extracted_html
# 清洗数据
def clean_data(bbs_list):
    print("夸父资源社>>> 开始清洗数据")
    save_data = []
    for bbs_info in bbs_list:
        extracted_html = get_detail(bbs_info)
        print("夸父资源社>>> 清洗数据,标题{}", bbs_info.title)
        quake_div = extracted_html.find('div', class_='alert alert-success')
        if quake_div:
            # 提取 a 标签的 href 属性
            a_tag = quake_div.find('a')
            if a_tag:
                href = a_tag.get('href')
                # 替换 a 标签为新的链接
                bbs_info.quake_old_href = href
            # 内容的前一个相邻元素
            quake_div.insert_before(quake_new)
            quake_div.decompose()

        # 假设要删除的div有特定的class，比如"message"
        divs_to_delete = extracted_html.find_all('div', class_='tt-license mt-3 position-relative overflow-hidden')
        for div in divs_to_delete:
            div.decompose()

        # 处理所有的img标签
        for img in extracted_html.find_all('img'):
            # 获取图片的src属性
            img_src = img.get('src')
            if img_src:  # 确保img标签有src属性
                # 检查src是否是完整的URL
                if not img_src.startswith('http'):
                    # 拼接完整的URL
                    img_src = base_url + img_src
                elif not img_src.startswith('https'):
                    img_src = base_url + img_src
            # 替换src属性为完整的URL
            img['src'] = img_src
        bbs_info.body = str(extracted_html)


        save_data.append(bbs_info)
    return save_data

# 数据持久化
def add_bbs_data(bbs_data):
    print("夸父资源社>>> 持久化数据")
    return BBSInfo.batch_add(bbs_data)

# 获取网页信息
def get_html_info(url):
    """
    获取网页信息
    :param url: 网页链接
    :return: 网页内容
    """
    try:
        # 发送 GET 请求 添加 cookie
        headers = {
            "cookie": cookie
        }
        response = requests.get(url, headers=headers)
        # 检查请求是否成功
        if response.status_code == 200:
            return response.text
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求出现异常: {e}")
# 回复帖子
def send_comment(code_number):
    """
    发送评论
    :param code_number: 帖子编号
    """
    url = f"{base_url}post-create-{code_number}-1.htm"
    headers = {
        "accept": "text/plain, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "cookie": cookie,
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    # 对中文进行 urlencoded 编码
    body = urlencode({
        "doctype": 1,
        "return_html": 1,
        "quoteid": 0,
        "message": "哈哈，不错哦！",
        "quick_reply_message": 1
    }, doseq=True)
    response = requests.post(url, headers=headers, data=body)
    return response
# 提取编码
def extract_number_from_url(url):
    # 使用正则表达式匹配数字
    match = re.search(r'\d+', url)
    if match:
        return match.group()
    else:
        return None

def start(uid, page=1):
    results = get_bbs_list(uid, page)
    save_data = clean_data(results)
    return add_bbs_data(save_data)

if __name__ == "__main__":
    # UID, 页数,
    start(2004,1)

# 1. 获取列表
# 2. 遍历详情
# 3. 判断是否已经评论
# 4. 清洗数据
# 5. 保存到数据库






