import time
from functools import lru_cache

import requests
from bs4 import BeautifulSoup

from FeiShu import add_record

# 创建游戏数据字典
game_data = {}
# 创建一个缓存字典
game_data_cache = {}


def parse_basic_info(soup):
    """
    获取游戏基本信息
    :param soup:
    :return:
    """
    # 提取标题
    title = soup.find("div", {"class": "apphub_AppName"})
    game_data["title"] = title.text.strip() if title else "No title found"

    # 提取封面图片URL
    header_image = soup.find("img", {"class": "game_header_image_full"})
    game_data["header_image_url"] = {"text": header_image['src'],
                                     "link": header_image['src']} if header_image else "No header image found"

    # 提取开发商
    developer = soup.find("div", {"id": "developers_list"})
    game_data["developer"] = developer.text.strip() if developer else "No developer found"

    # 提取发行商
    publisher = soup.find("div", class_="dev_row").find_next("div", class_="summary column")
    game_data["publisher"] = publisher.text.strip() if publisher else "No publisher found"

    # 提取发行日期
    release_date = soup.find("div", class_="date")
    game_data["release_date"] = release_date.text.strip() if release_date else "No release date found"

    # 提取游戏描述
    description = soup.find("div", class_="game_description_snippet")
    game_data["description"] = description.text.strip() if description else "No description found"

    # 提取用户标签
    tags = soup.find_all("a", class_="app_tag")
    game_data["tags"] = [tag.text.strip() for tag in tags] if tags else []

    # 提取用户评分
    recent_review = soup.find("div", class_="user_reviews_summary_row")
    game_data["recent_review"] = recent_review.text.strip() if recent_review else "No recent review found"

    all_reviews = soup.find("div", {"itemprop": "aggregateRating"})
    game_data["all_reviews"] = all_reviews.text.strip() if all_reviews else "No all reviews found"

    # 类型
    types = [a.text for a in soup.select('b:contains("类型:") + span a')]
    game_data["types"] = types if types else []


def parse_game_info(soup):
    """
    获取游戏详细信息
    :param soup:
    :return:
    """
    # 游戏截图
    images = soup.find("div", {"id": "highlight_player_area"}).find_all("a", {"class": "highlight_screenshot_link"})
    # for i in images:
    #     print(i["href"])

    # 600 x 338
    game_data["image_urls"] = [image["href"].replace(".1920x1080.", ".600x338.") for image in images] if images else []

    # 过滤掉指定内容的记录
    for image in images:
        if str(image).endswith("blank.gif"):
            images.remove(image)

    # 关于游戏
    about_game = soup.find("div", {"id": "game_area_description"})

    if about_game:
        about_game['style'] = (
            "line-height: 1.5em; "
            "font-size: 14px; "
            "margin-top: 30px; "
            "overflow: hidden; "
            "max-width: 100%; "
            "font-family: 'Motiva Sans', Sans-serif; "
            "font-weight: normal;"
        )

    # 找到所有img添加指定样式
    for img in about_game.find_all("img"):
        img['style'] = (
            "display: block; "
            "margin-left: auto; "
            "margin-right: auto; "
        )

    about_game.find("h2")['style'] = (
        "scroll-behavior: auto !important; box-sizing: border-box; margin: 25px 0px 20px; font-family: HarmonyOS_Regular; font-weight: bold; line-height: 17px; color: rgb(33, 37, 41); font-size: 18px; border-left: 4px solid rgb(0, 123, 245); padding: 0px 0px 0px 10px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;"
    )

    game_data["about_game"] = (str(about_game).replace("\xa0", "")
                               .replace("\t", "")
                               .replace("h2", "h3")
                               .replace("\n", "")
                               .replace("\r", "")
                               .replace("<p class=\"bb_paragraph\"></p>", "")
                               # .replace("\\<br\\>","")
                               ) if about_game else "No about game found"

    # 游戏配置
    # 提取最低配置和推荐配置
    # minimum_requirements = soup.find('div', class_='game_area_sys_req_leftCol').find_all('li')

    # recommended_requirements = soup.find("div", class_="game_area_sys_req_rightCol").find_all('li')

    # game_data["minimum_requirements"] = minimum_requirements
    # game_data["recommended_requirements"] = recommended_requirements

@lru_cache(maxsize=128)  # 最大缓存128个条目
def fetch_steam_app_info(app_id):
    # 检查缓存是否有该游戏数据
    if app_id in game_data_cache:
        return game_data_cache[app_id]

    url = f"https://store.steampowered.com/app/{app_id}"

    game_data["steam_url"] = {
        "text": url,
        "link": url
    }

    # 设置User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # 设置返回内容为中文
    cookie = {
        "Steam_Language": "schinese"
    }

    # 发送HTTP请求
    response = requests.get(url, headers=headers, cookies=cookie, allow_redirects=False)
    if response.status_code != 200:
        return None

    # 手动设置编码
    response.encoding = 'utf-8'  # 根据实际情况设置编码

    # 解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')

    parse_basic_info(soup)

    parse_game_info(soup)

    # 将结果存入缓存
    game_data_cache[app_id] = game_data

    return game_data


def get_game_data(data):
    """
    对外接口
    :return:
    """
    steam_info = fetch_steam_app_info(data["appId"])

    steam_info.update(data)
    # 生成bbs内容
    steam_info = generate_bbs_content(steam_info)

    return steam_info


def generate_bbs_content(data):
    htm = f"""<body id="tinymce" class="mce-content-body " data-id="message" aria-label="编辑区。按Alt+0键打开帮助。"
      contenteditable="true" spellcheck="false"
      style="overflow-y: hidden; padding-left: 1px; padding-right: 1px; min-height: 0px;"
      data-mce-style="overflow-y: hidden; padding-left: 1px; padding-right: 1px; min-height: 0px;"><h5
        style="scroll-behavior: auto !important; box-sizing: border-box; margin: 0px 0px 15px; font-family: HarmonyOS_Regular; font-weight: 600; line-height: 1.2; color: rgb(51, 51, 51); font-size: 16px; background: rgb(235, 237, 242); padding: 5px 10px 6px; border-left: 4px solid rgb(202, 203, 203); border-radius: 5px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;">
    夸克网盘下载</h5>
    <p style="text-align: center;">[ttreply]链接：<span style="color: #234cee;"></span><a
        href="{data.get("quarkLink", {}).get("link", "")}" target="_blank" rel="nofollow noopener"><span
        style="color: #234cee;">{data.get("quarkLink", {}).get("link", "")}</span></a> [/ttreply]</p>
    <p><img class="" style="display: block; margin-left: auto; margin-right: auto;"
        src="{data["header_image_url"]["link"]}"></p>
    """

    htm += f"""
    <table style="border-collapse: collapse; width: 100.02%; height: 63.4287px; border-width: 0px; font-size: 14px;" border="0">
    <colgroup>
        <col style="width: 49.9314%;">
        <col style="width: 49.9314%;">
    </colgroup>
    <tbody>
    <tr style="height: 21.1429px;">
        <td style="height: 21.1429px; border-width: 0px;">游戏名称：{data["title"]}</td>
        <td style="height: 21.1429px; border-width: 0px;">发行商：{data["publisher"]}</td>
    </tr>
    <tr style="height: 21.1429px;">
        <td style="height: 21.1429px; border-width: 0px;">发行日期：{data["release_date"]}</td>
        <td style="height: 21.1429px; border-width: 0px;">开发商：{data["developer"]}</td>
    </tr>
    <tr style="height: 21.1429px;">
        <td style="border-width: 0px; height: 21.1429px;">游戏类型：{", ".join(data["types"][:3])}独立, 模拟</td>
        <td style="border-width: 0px; height: 21.1429px;">游戏标签：{", ".join(data["tags"][:3])}交通运输，模拟</td>
    </tr>
    </tbody>
    </table>
    <h3 style="scroll-behavior: auto !important; box-sizing: border-box; margin: 25px 0px 20px; font-family: HarmonyOS_Regular; font-weight: bold; line-height: 17px; color: rgb(33, 37, 41); font-size: 18px; border-left: 4px solid rgb(0, 123, 245); padding: 0px 0px 0px 10px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;">
    游戏简介</h3>
    <p>{data["description"]}</p>
    <h3 style="scroll-behavior: auto !important; box-sizing: border-box; margin: 25px 0px 20px; font-family: HarmonyOS_Regular; font-weight: bold; line-height: 17px; color: rgb(33, 37, 41); font-size: 18px; border-left: 4px solid rgb(0, 123, 245); padding: 0px 0px 0px 10px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;">
    游戏截图</h3>
    """
    # 游戏截图
    limited_urls = data["image_urls"][:6]
    html_snippets = []
    for i in range(0, len(limited_urls), 2):
        # 处理每对图片，确保不会越界
        img1 = f'<img style="transition: none;" src="{limited_urls[i]}" alt="{limited_urls[i]}" width="380" height="213">'
        if i + 1 < len(limited_urls):
            img2 = f'<img style="transition: none;" src="{limited_urls[i + 1]}" alt="{limited_urls[i + 1]}" width="380" height="213">'
            html_snippets.append(f'<p>{img1} {img2}</p>')
        else:
            html_snippets.append(f'<p>{img1}</p>')

    htm += ''.join(html_snippets)

    # 关于游戏
    htm += data["about_game"]
    # 系统需求
    # 表格模板
    # htm += f'''
    # <h3 style="scroll-behavior: auto !important; box-sizing: border-box; margin: 25px 0px 20px; font-family: HarmonyOS_Regular; font-weight: bold; line-height: 17px; color: rgb(33, 37, 41); font-size: 18px; border-left: 4px solid rgb(0, 123, 245); padding: 0px 0px 0px 10px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;">系统需求</h3>
    # <table border="0" style="border-collapse: collapse; width: 100%;">
    # <colgroup><col style="width: 20%;"><col style="width: 40%;"><col style="width: 40%;"></colgroup>
    # <thead>
    # <tr>
    # <th></th>
    # <th>最低配置</th>
    # <th>推荐配置</th>
    # </tr>
    # </thead>
    # <tbody>
    # <tr>
    # <td>操作系统</td>
    # <td>{data["minimum_requirements"][1].get_text().split(':')[-1].strip()}</td>
    # <td>{data["recommended_requirements"][1].get_text().split(':')[-1].strip()}</td>
    # </tr>
    # <tr>
    # <td>处理器</td>
    # <td>{data["minimum_requirements"][2].get_text().split(':')[-1].strip()}</td>
    # <td>{data["recommended_requirements"][2].get_text().split(':')[-1].strip()}</td>
    # </tr>
    # <td>内存</td>
    # <td>{data["minimum_requirements"][3].get_text().split(':')[-1].strip()}</td>
    # <td>{data["recommended_requirements"][3].get_text().split(':')[-1].strip()}</td>
    # </tr>
    # <td>显卡</td>
    # <td>{data["minimum_requirements"][4].get_text().split(':')[-1].strip()}</td>
    # <td>{data["recommended_requirements"][4].get_text().split(':')[-1].strip()}</td>
    # </tr>
    # <td>DirectX 版本</td>
    # <td>{data["minimum_requirements"][5].get_text().split(':')[-1].strip()}</td>
    # <td>{data["recommended_requirements"][5].get_text().split(':')[-1].strip()}</td>
    # </tr>
    # <td>存储空间</td>
    # <td>{data["minimum_requirements"][7].get_text().split(':')[-1].strip()}</td>
    # <td>{data["recommended_requirements"][7].get_text().split(':')[-1].strip()}</td>
    # </tr>
    # </tbody></table>'''

    # 注意事项
    if data.get("remarks","") != "":
        htm += f"""
        <h3 style="scroll-behavior: auto !important; box-sizing: border-box; margin: 25px 0px 20px; font-family: HarmonyOS_Regular; font-weight: bold; line-height: 17px; color: rgb(33, 37, 41); font-size: 18px; border-left: 4px solid rgb(0, 123, 245); padding: 0px 0px 0px 10px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;">
        注意事项</h3>
        {data.get("remarks","")}
        """
    htm += f"""
    </body>
    """

    data["bbs_content"] = htm

    # 标题生成
    data["bbs_title"] = f"{data['title']}  {data['version']} 【{data['size']}】"

    return data



# # # 示例用法
# app_id = "1172470"
# # # # 添加游戏数据到飞书多维表格中
# fetch_steam_app_info(app_id)
# # print(game_data["minimum_requirements"])
#
# generate_bbs_content(game_data)
#
#
# print(game_data["about_game"])
# add_record(game_data)

# 测试缓存功能
if __name__ == "__main__":
    app_id = "570"  # 比如DOTA 2的Steam ID
    start_time = time.time()
    result1 = fetch_steam_app_info(app_id)
    print(result1)
    print(f"First fetch time: {time.time() - start_time} seconds")

    # 再次调用，应该更快
    start_time = time.time()
    result2 = fetch_steam_app_info(app_id)
    print(result2)
    print(f"Second fetch time (cached): {time.time() - start_time} seconds")