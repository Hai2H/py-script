import base64
import io
import re

import chardet
import requests
from PIL import Image
from bs4 import BeautifulSoup

class KuaFu:

    def __init__(self, bbs_info):
        self.session = requests.Session()
        self.cookie = ("__51vcke__KftoURhw1leQPNWu=331e5dee-b936-5c49-bec5-acf980aef442; __51vuft__KftoURhw1leQPNWu=1736821755157; cf_clearance=ZK.NZp2.85Uz2xo2lbCnBfCSwkgAFDcCcGWL6CRaumY-1736923939-1.2.1.1-BRG1Xv43SSbRrZ3Pbpy8YlYh8Ehefq4cDLXQlSlt2XX_RS79J8Pp2jhuHdTBTAegAzjf4B2N4uYOvjRuk1VDTr8aX3S8kOGyv2FJs9ToI3hehzkeGbIV3mEZo_WfPVOfavCfCgliJGcKIioh3cQ3lqoDYBxIXeJoFbXxL68Yn97IdyeTaWOab.6yr7WczH8vyKY88MxRscOZzFscA_rdSlktzN1KMfw2iMhfK.3RKbfdncQVRunCxD2cLxQKc5G.4u5wAetnz1J0GW8vnldNH_JmJ_gCJISOWoO_0TMy7SQ; __51huid__Jf4VdJkTv7WGYSPa=cb7c2828-1619-5530-8c7a-2295d4e25376; __gads=ID=d20b8aabd0a417a6:T=1739927057:RT=1739927057:S=ALNI_MZX9otfElEHmb4pOVd6X_VHXpGhfg; __gpi=UID=00001040eb268ae1:T=1739927057:RT=1739927057:S=ALNI_MaEiJa8qM6B2Rtai8M16AYX4o8siA; __eoi=ID=9e9108323197fa00:T=1739927057:RT=1739927057:S=AA-Afjb6d9TRTgiYe6kUbPDOBqyc; bbs_token=FE6pdYMmKch6eRU8bQ4cR2ZUuIZxBXUibuQvStWBXfJeVD4A; bbs_sid=k1fd4gjrblis95ppu36ion1h57; __51uvsct__KftoURhw1leQPNWu=77; __vtins__KftoURhw1leQPNWu=%7B%22sid%22%3A%20%22312e06d7-1a78-5e70-b444-281490aad399%22%2C%20%22vd%22%3A%202%2C%20%22stt%22%3A%207238%2C%20%22dr%22%3A%207238%2C%20%22expires%22%3A%201741146578474%2C%20%22ct%22%3A%201741144778474%7D")
        self.headers = {
            'scheme': 'https',
            'accept': 'text/plain, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br,zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
            'origin': 'https://www.kuafuzy.com',
            'pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
            'Cookie': self.cookie
        }

        self.add_url = 'https://www.kuafuzy.com/thread-create-1.htm'
        self.update_url = 'https://www.kuafuzy.com/post-update'
        self.upload_file_url = 'https://www.kuafuzy.com/attach-create.htm'

        self.nodeMap ={
            "电影区": {
                "code": 1,
                "喜剧": 1,
                "爱情": 3,
                "剧情": 4,
                "科幻": 5,
                "悬疑": 6,
                "动画": 7,
                "犯罪": 8,
                "惊悚": 9,
                "冒险": 10,
                "奇幻": 11,
                "恐怖": 12,
                "战争": 13,
                "灾难": 14,
                "动作": 181,
                "中国大陆": 2,
                "中国香港": 16,
                "中国台湾": 17,
                "美国": 18,
                "韩国": 19,
                "日本": 20,
                "英国": 21,
                "法国": 22,
                "泰国": 23,
                "印度": 24,
                "其他": 25
            },
            "剧集区": {
                "code": 2,
                "喜剧": 26,
                "爱情": 28,
                "悬疑": 29,
                "武侠": 30,
                "古装": 31,
                "犯罪": 32,
                "科幻": 33,
                "恐怖": 34,
                "战争": 35,
                "动作": 36,
                "冒险": 37,
                "剧情": 38,
                "奇幻": 39,
                "综艺": 40,
                "中国大陆": 27,
                "中国香港": 41,
                "中国台湾": 42,
                "美国": 43,
                "韩国": 44,
                "日本": 45,
                "英国": 46,
                "德国": 47,
                "法国": 48,
                "泰国": 49,
                "其他": 50
            },
            "4K电影": {
                "code": 3,
                "4K REMUX": 51,
                "WEB-DL 4K": 54,
                "4K UHD原盘": 55,
                "杜比视界": 56,
                "SDR": 57,
                "HDR": 58,
                "蓝光BluRay": 59,
                "喜剧": 52,
                "爱情": 61,
                "动作": 62,
                "科幻": 63,
                "悬疑": 64,
                "灾难": 65,
                "犯罪": 66,
                "惊悚": 67,
                "冒险": 68,
                "奇幻": 69,
                "历史": 70,
                "恐怖": 71,
                "战争": 72,
                "剧情": 73,
                "中国大陆": 53,
                "中国香港": 75,
                "中国台湾": 76,
                "美国": 77,
                "韩国": 78,
                "日本": 79,
                "英国": 80,
                "法国": 81,
                "泰国": 82,
                "印度": 83,
                "其他": 84
            },
            "4K剧集": {
                "code": 4,
                "4K REMUX": 85,
                "WEB-DL 4K": 88,
                "其他4K": 89,
                "SDR": 90,
                "HDR": 91,
                "杜比视界": 92,
                "蓝光BluRay": 93,
                "喜剧": 86,
                "爱情": 94,
                "悬疑": 95,
                "恐怖": 96,
                "古装": 97,
                "犯罪": 98,
                "科幻": 99,
                "战争": 100,
                "动作": 101,
                "冒险": 102,
                "剧情": 103,
                "奇幻": 104,
                "惊悚": 105,
                "中国大陆": 87,
                "中国香港": 107,
                "中国台湾": 108,
                "美国": 109,
                "韩国": 110,
                "日本": 111,
                "英国": 112,
                "法国": 113,
                "泰国": 114,
                "其他": 115
            },
            "动漫区": {
                "code": 5,
                "励志": 116,
                "热血": 117,
                "战斗": 118,
                "校园": 120,
                "恋爱": 121,
                "治愈": 122,
                "奇幻": 123,
                "推理": 124,
                "科幻": 125,
                "搞笑": 126,
                "冒险": 127,
                "中国": 119,
                "日本": 129,
                "韩国": 130,
                "欧美": 131
            },
            "短剧区": {
                "code":6
            },
            "书籍区": {
                "code": 7,
                "电子书": 132,
                "有声书": 134,
                "文学": 133,
                "小说": 135,
                "生活": 136,
                "历史文化": 137,
                "陈工励志": 138,
                "经济管理": 139,
                "科技科普": 140,
                "计算机与互联网": 141,
                "漫画绘本": 142,
                "合集": 143
            },
            "音乐区": {
                "code": 8,
                "华语": 144,
                "日韩": 145,
                "欧美": 146,
                "Remix": 147,
                "纯音乐": 148,
                "异次元": 149,
                "无损合集": 150,
                "专辑": 151
            },
            "软件区": {
                "code": 9,
            },
            "游戏区": {
                "code": 10,
                "动作冒险": 159,
                "模拟经营": 161,
                "角色扮演": 162,
                "枪战射击": 163,
                "恐怖惊悚": 164,
                "体育竞速": 165,
                "休闲益智": 166,
                "策略战旗": 167,
                "即时战略": 168
            },
            "学习区": {
                "code": 11,
            },
            "资源杂烩": {
                "code": 12,
            },
            "纪录片": {
                "code": 13,
            },
            "综艺区": {
                "code": 14,
            },
            "站务区": {
                "code": 15,
            },
            "互助悬赏": {
                "code": 16,
            }
        }

        self.doctype = 0
        self.quotepid = 0
        self.subject = bbs_info.title
        self.message = bbs_info.body
        self.httpurl = ""
        self.vodurl = ""
        # 栏目
        self.fid = self.get_node_id(bbs_info.node)
        self.tagid = self.get_tag_ids(bbs_info.node, bbs_info.tags)


    def get_node_id(self, node):
        """
        获取节点的ID
        :param node: 节点名称
        :return: 节点ID
        """
        if node in self.nodeMap:
            return self.nodeMap[node]['code']
        else:
            return 0

    def get_tag_ids(self, node, tags):
        """
        获取标签的ID列表
        :param node: 节点名称
        :param tags: 标签名称列表
        :return: 标签ID列表
        """
        if tags is None:
            return []
        if node in self.nodeMap:
            tagsMap = self.nodeMap[node]
            tagsSplit = tags.split(',')
            tagids = []
            for tag in tagsSplit:
                if tag in tagsMap:
                    tagids.append(tagsMap[tag])
            return tagids
        else:
            return []

    def add_kuafu(self):
        """
        添加资源记录
        :return: 结果
        """
        print("夸父资源>>> 添加新记录")
        self.upload_images_and_replace()
        data = {
            'doctype': self.doctype,
            'quotepid': self.quotepid,
            'subject': self.subject,
            'message': self.message,
            'httpurl': self.httpurl,
            'vodurl': self.vodurl,
            'fid': self.fid,
            'tagid[]': self.tagid
        }
        response = self.session.post(self.add_url, headers=self.headers, data=data)
        if response.status_code == 302:
            return "被重定向了"

        print("夸父资源>>> "
              "请求地址：", response.request.url,
              "请求头部：", response.request.headers,
              "请求方法：", response.request.method,
              "请求数据：", response.request.body,
              )
        response_html = response.content.decode('utf-8')

        if "发帖成功" in response_html:
            return "发帖成功"
        else:
            if "用户登录" in response_html:
                return "登录过期"
            return "发帖失败"

    def update_kuafu(self, id):
        """
        更新资源记录
        :param id: 资源ID
        :return: 结果
        """
        print("夸父资源>>> 更新记录")
        self.upload_images_and_replace()
        data = {
            'doctype': self.doctype,
            'quotepid': self.quotepid,
            'subject': self.subject,
            'message': self.message,
            'httpurl': self.httpurl,
            'vodurl': self.vodurl,
            'fid': self.fid,
            'tagid[]': self.tagid
        }
        response = self.session.post(self.update_url + '-' + str(id) + '.htm', headers=self.headers, data=data)

        if response.status_code == 302:
            return "被重定向了"

        print("夸父资源>>> "
              "请求地址：", response.request.url,
              "请求头部：", response.request.headers,
              "请求方法：", response.request.method,
              "请求数据：", response.request.body,
              )
        response_html = response.content.decode('utf-8')

        if "发帖成功" in response_html:
            return "更新成功"
        else:
            if "用户登录" in response_html:
                return "登录过期"
            return "更新失败"

    def upload_images_and_replace(self):
        """
        转换图片地址
        """
        soup = BeautifulSoup(self.message, 'html.parser')

        img_tags = soup.find_all('img')

        for img in img_tags:
            old_src = img['src']
            try:
                # 请求图片资源
                response = self.session.get(old_src, headers=self.headers)
                image_data = response.content

                # 使用 Pillow 打开图片并获取长宽
                with Image.open(io.BytesIO(image_data)) as img_obj:
                    width, height = img_obj.size

                # 从 URL 中提取图片名字
                name = old_src.split('/')[-1]
                # 从 URL 中提取图片名字和扩展名
                ext = name.split('.')[-1].lower()

                # 根据扩展名确定 MIME 类型
                mime_type = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif'
                }.get(ext, 'image/jpeg')

                # 将图片数据编码为 Base64 字符串
                base64_image = base64.b64encode(image_data).decode('utf-8')
                data = {
                    'is_image': 1,
                    'width': width,
                    'height': height,
                    'name': name,
                    'data': f'data:{mime_type};base64,{base64_image}'
                }
                # 上传图片
                upload_response = self.session.post(self.upload_file_url, headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.kuafuzy.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
                    'Cookie': self.cookie
                }, data=data)
                # 检查请求是否成功（如果状态码不是200系列，会抛出异常）
                upload_response.raise_for_status()

                # 检测响应内容的编码
                encoding = chardet.detect(upload_response.content)['encoding']
                # 根据检测出的编码设置响应的编码并获取文本内容
                upload_response.encoding = encoding
                html_content = upload_response.text
                # 定义正则表达式模式返回的结构 {}
                pattern = r'\[(\w+)\]\s*=>\s*([^\s\]]+)'
                # 查找所有匹配项
                matches = re.findall(pattern, html_content)
                # 构建字典
                array_data = {key: value for key, value in matches}
                print("夸父资源>>> 图片上传回显参数", array_data)
                url = array_data['url']
                # 清空img标签的其他属性
                img.attrs = {}
                img['src'] = url
                img['width'] = width
                img['height'] = height

            except requests.RequestException as e:
                print(f"处理图片 {old_src} 时出错: {e}")
            except Exception as e:
                print(f"处理图片 {old_src} 时发生未知错误: {e}")

        print("夸父资源>>>",str(soup))
        self.message = str(soup)