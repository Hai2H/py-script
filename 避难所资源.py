import cloudscraper
import time
import random
import json
from venv import logger
from bs4 import BeautifulSoup
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

app_id = 'cli_a7bee94bee01d00d'
app_secret = 'PPCFxdAZ5r6iGwGwHwVPoh85TfSPeYXp'
# 创建飞书 client
client = lark.Client.builder() \
    .app_id(app_id) \
    .app_secret(app_secret) \
    .log_level(lark.LogLevel.DEBUG) \
    .build()

def test():
    # 创建一个cloudscraper实例
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        },
        delay=10
    )
    # 获取页面内容
    response = scraper.get('https://www.flysheep6.com/page/1', timeout=30)
    response.raise_for_status()
    print(response.text)



def get_resource_list(num):
    """
    获取避难所资源列表
    """
    # 创建一个cloudscraper实例
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        },
        delay=10
    )
    
    blog_records = []
 
    print(f'正在抓取第{num}页')
    url = f'https://www.flysheep6.com/page/{num}'
    
    try:
        # 获取列表页
        response = scraper.get(url, timeout=30)
        response.raise_for_status()
        
        # 解析列表页
        soup = BeautifulSoup(response.text, 'html.parser')
        blog_posts = soup.select('div.blog-listing')
        
        for post in blog_posts:
            try:
                # 提取基本信息
                title_element = post.select_one('.entry-title a')
                title = title_element.text.strip()
                link = title_element['href']
                img_url = post.select_one('.entry-thumbnail img')['src']
                            
                # 创建记录
                blog_info = {
                    '标题': title,
                    '封面图片链接': {
                        'text': img_url,
                        'link': img_url
                    },
                    '网址链接': {
                        'text': link,
                        'link': link
                    },
                    '发布日期': post.select_one('.entry-date a').text.strip(),
                    '内容摘要': post.select_one('.entry-content p').text.strip() if post.select_one('.entry-content p') else '无摘要'
                }
                
                # 添加延时，避免请求过快
                time.sleep(random.uniform(3, 5))

                # 获取详情页
                detail_response = scraper.get(link, timeout=30)
                detail_response.raise_for_status()
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                # 提取夸克链接
                # 匹配到  href="https://pan.quark.cn/s/9fa1802f9543" 格式的链接
                href_element = detail_soup.select_one('a[href^="https://pan.quark.cn/s/"]')
                if href_element:
                    blog_info['夸克链接'] = {
                        'text': href_element['href'],
                        'link': href_element['href']
                    }
                
                blog_records.append(blog_info)
                print(f'成功抓取: {title}')
                
            except Exception as e:
                print(f'处理详情页出错: {str(e)}')
                continue
                
        # 每页完成后添加延时
        time.sleep(random.uniform(5, 8))
        
    except Exception as e:
        print(f'处理列表页出错: {str(e)}')
        return blog_records

    return blog_records


def add_records_to_feishu(records):
    logger.info("开始添加飞书记录")
    if len(records) == 0:
        logger.info("没有数据")
        return
    
       # 构造请求对象
    request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .table_id("tblOC82ROIr8mgTP") \
        .request_body(BatchCreateAppTableRecordRequestBody.builder()
            .records([
               AppTableRecord.builder()
               .fields(records[i])
               .build() for i in range(len(records))  # 使用列表推导式构造记录
           ])
            .build()) \
        .build()

    # 发起请求
    response: BatchCreateAppTableRecordResponse = client.bitable.v1.app_table_record.batch_create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.batch_create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

def update_records_to_feishu(records):
    logger.info("开始更新飞书记录")
    if len(records) == 0:
        logger.info("没有数据")
        return
    
    request: BatchUpdateAppTableRecordRequest = BatchUpdateAppTableRecordRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .table_id("tblOC82ROIr8mgTP") \
        .request_body(BatchUpdateAppTableRecordRequestBody.builder()
            .records([
                AppTableRecord.builder()
                .fields({
                    '夸克链接': {
                        'text': record.get('夸克链接', {'text': '', 'link': ''})['text'],
                        'link': record.get('夸克链接', {'text': '', 'link': ''})['link']
                    }
                })
                .record_id(record['record_id'])
                .build()
                for record in records
            ])
            .build()) \
        .build()

    # 发起请求
    response: BatchUpdateAppTableRecordResponse = client.bitable.v1.app_table_record.batch_update(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.batch_update failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

def get_records_from_feishu(urls):
    """
    获取飞书记录
    urls: list 需要查询的网址链接列表
    """
    logger.info("开始查询飞书记录")
     # 构造请求对象
    request: SearchAppTableRecordRequest = SearchAppTableRecordRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .table_id("tblOC82ROIr8mgTP") \
        .request_body(SearchAppTableRecordRequestBody.builder()
            .view_id("vewMB7HioH")
            .field_names(["标题", "网址链接", "夸克链接"])
            .sort([])
            .filter(FilterInfo.builder()
                .conjunction("or")
                .conditions([
                    Condition.builder()
                        .field_name("网址链接")
                        .operator("is")
                        .value([url])
                        .build()
                    for url in urls
                ])
                .build())
            .automatic_fields(False)
            .build()) \
        .build()

    # 发起请
    response: SearchAppTableRecordResponse = client.bitable.v1.app_table_record.search(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    # 处理响应结果
    if response.success():
        return extract_records_from_feishu(response.data)

def extract_records_from_feishu(response_data):
    """
    从响应数据中提取记录信息
    """
    records = []
    for item in response_data.items:
        record = {
            'record_id': item.record_id,
            '标题': item.fields.get('标题')[0],
            '网址链接': item.fields.get('网址链接', {}),
            '夸克链接': item.fields.get('夸克链接', {'text': '', 'link': ''})
        }
        records.append(record)
    return records


def start(start_page=1, end_page=1):
    """
    添加记录
    """
    # 获取避难所资源列表
    for i in range(start_page, end_page + 1):
        data = get_resource_list(i)
        # 获取避难所所存在的飞书记录
        if not data:
            return
        feishu_records = get_records_from_feishu([item['网址链接']['link'] for item in data])
        
        # 筛选出需要更新的记录
        update_records = []
        for item in data:
            for record in feishu_records:
                if item['网址链接']['text'] == record['网址链接']['text']:
                    # 检查夸克链接是否存在且不一致
                    item_quark = item.get('夸克链接', {}).get('text', '')
                    record_quark = record.get('夸克链接', {}).get('text', '')
                    if item_quark != record_quark:
                        item['record_id'] = record['record_id']
                        update_records.append(item)
                    break
        
        # 新增记录
        add_records = []
        existing_urls = {record['网址链接']['text'] for record in feishu_records}
        for item in data:
            if item['网址链接']['text'] not in existing_urls:
                add_records.append(item)
        
        # 更新记录
        if update_records:
            update_records_to_feishu(update_records)

        # 新增记录
        if add_records:
            add_records_to_feishu(add_records)


    
if __name__ == '__main__':
    # 批量获取当前资源列表
    start(start_page=1, end_page=3)


    