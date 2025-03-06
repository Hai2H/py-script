import base64
import io
import re

import chardet
import requests
from PIL import Image
from bs4 import BeautifulSoup

if __name__ == '__main__':
    soup = BeautifulSoup("""
                <div class="message break-all" isfirst="1">
<p><img alt="小学作文素材资料包【3.5GB】" src="https://www.kuafuzys.com/upload/attach/202501/101680_N39633GTUUB3GEH.png"/></p>
<p> </p>{quake_new_url}

</div>

    """, 'html.parser')
    img_tags = soup.find_all('img')

    for img in img_tags:
        old_src = img['src']
        print(old_src)
        try:
            # 请求图片资源
            response = requests.get(old_src)
            # response.raise_for_status()
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
            upload_response = requests.post('https://www.kuafuzy.com/attach-create.htm', headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': 'www.kuafuzy.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
                'Cookie': "bbs_token=5UGTLT08Qcrv_2FKisPY6_2B_2BpaoyeciGm6YJxqyd_2B9OlCIkRk_2F6;bbs_sid=pk1got5rva550rtmemleg1m6o6"
            }, data=data)
            # 检查请求是否成功（如果状态码不是200系列，会抛出异常）
            upload_response.raise_for_status()

            # 检测响应内容的编码
            encoding = chardet.detect(upload_response.content)['encoding']
            # 根据检测出的编码设置响应的编码并获取文本内容
            upload_response.encoding = encoding
            html_content = upload_response.text

            # 定义正则表达式模式
            pattern = r'\[(\w+)\]\s*=>\s*([^\s\]]+)'

            # 查找所有匹配项
            matches = re.findall(pattern, html_content)

            # 构建字典
            array_data = {key: value for key, value in matches}

            print(array_data)

            # 假设响应文本就是新的图片地址
            # new_src = upload_response.json()
            # print(new_src)
            img['src'] = array_data['url']
        except requests.RequestException as e:
            print(f"处理图片 {old_src} 时出错: {e}")
        except Exception as e:
            print(f"处理图片 {old_src} 时发生未知错误: {e}")
        print(img)