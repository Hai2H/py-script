import json

from venv import logger

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

app_id = 'cli_a7bee94bee01d00d'
app_secret = 'PPCFxdAZ5r6iGwGwHwVPoh85TfSPeYXp'

def add_record(data):
    """
    添加记录
    :return:
    """
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()
    d = transform_to_feishu_format(data)
    logger.info(d)
    # 构造请求对象
    request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .table_id("tblcwsYexPyqGxpk") \
        .request_body(AppTableRecord.builder()
                      .fields(d)
                      .build()) \
        .build()

    # 发起请求
    response: CreateAppTableRecordResponse = client.bitable.v1.app_table_record.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return False

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    return True


def transform_to_feishu_format(input_json):
    """
    将采集的 JSON 数据转换成飞书所需的字段格式。
    """
    # 字段映射
    field_mapping = {
        "steam_url": "Steam",
        "title": "游戏名称",
        "header_image_url": "封面图片",
        "developer": "开发商",
        "publisher": "发行商",
        "release_date": "发行日期",
        "description": "游戏描述",
        "tags": "用户标签",
        "recent_review": "用户评分",
        "types": "类型",
        "all_reviews": "用户评论",
        "image_urls": "游戏截图",
        "about_game": "关于游戏",
        "minimum_requirements": "最低配置",
        "recommended_requirements": "推荐配置",
        "version":"版本",
        "resourceLink":"资源链接",
        "quarkLink":"夸克分享链接",
        "size":"资源大小",
        "bbs_content":"文章内容",
        "bbs_title":"文章标题",
    }

    # 创建一个新的字典用于存储转换后的数据
    transformed_data = {}

    # 遍历字段映射，将源字段数据转换为目标字段格式
    for source_field, target_field in field_mapping.items():
        if source_field in input_json:
            transformed_data[target_field] = input_json[source_field]

    logger.info(transformed_data)
    return transformed_data




# SDK 使用说明: https://github.com/larksuite/oapi-sdk-python#readme
# 以下示例代码是根据 API 调试台参数自动生成，如果存在代码问题，请在 API 调试台填上相关必要参数后再使用
# 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
def main():
    """
    测试SDK
    :return:
    """
    # 创建client
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 多维文档信息
    request: GetAppRequest = GetAppRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .build()

    # 发起请求
    response: GetAppResponse = client.bitable.v1.app.get(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    # 获取多维文档表格信息
    request: ListAppTableRequest = ListAppTableRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .build()

    # 发起请求
    response: ListAppTableResponse = client.bitable.v1.app_table.list(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    # 构造请求对象
    request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
        .app_token("UPIVbdUrtalakDsHMmncnI78nzg") \
        .table_id("tblcwsYexPyqGxpk") \
        .request_body(AppTableRecord.builder()
                      .fields({"游戏名称": "233"})
                      .build()) \
        .build()

    # 发起请求
    response: CreateAppTableRecordResponse = client.bitable.v1.app_table_record.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))



if __name__ == "__main__":
    main()
