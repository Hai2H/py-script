from datetime import datetime

import pytz
from flask import Flask, render_template, request
from flask_cors import CORS  # 导入 CORS 支持
import logging

from api import FeiShu, SteamInfo
from api.KuaFu import KuaFu
from database import BBSInfo
from tool import KuafuzysAcquisition

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域访问，可以指定域名

# 配置日志
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

def format_datetime(value, format='%Y-%m-%d'):
    from datetime import datetime
    if isinstance(value, (int, float)):
        tz = pytz.timezone('Asia/Shanghai')  # 可以根据需要修改时区
        date_time = datetime.fromtimestamp(value, tz)
        return date_time.strftime(format)
    return value

app.jinja_env.filters['datetime'] = format_datetime


@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# 使用 before_request 替代 before_first_request
@app.before_request
def log_request():
    app.logger.info("收到新的请求")

@app.route('/')
def home():  # put application's code here
    app.logger.info("访问首页")
    return render_template("index.html")

@app.route('/add_feishu_record', methods=['POST'])
def add_record():
    data = request.get_json()
    app.logger.info(f"收到添加记录请求: {data}")
    game_data = SteamInfo.get_game_data(data)
    app.logger.info(f"处理后的游戏数据: {game_data}")
    if FeiShu.add_record(game_data):
        app.logger.info("添加记录成功")
        return "添加成功"
    else:
        app.logger.error("添加记录失败")
        return "添加失败"

@app.route('/steam_name/<appID>', methods=['GET'])
def steam_name(appID):
    app.logger.info(f"查询游戏名称: {appID}")
    game_data = SteamInfo.fetch_steam_app_info(appID)
    if game_data and "title" in game_data:
        app.logger.info(f"找到游戏: {game_data['title']}")
        return game_data["title"]
    else:
        app.logger.warning(f"未找到游戏: {appID}")
        return "游戏名称未找到"


@app.route('/original', methods=['GET'])
def original():
    return render_template("original.html")
@app.route('/repost', methods=['GET'])
def repost():
    """
    资源搬运
    """
    # 获取参数
    page = request.args.get('page', type=int, default=1)
    result = BBSInfo.paginate(page=page)
    # 数据总条数
    total = BBSInfo.get_total()
    pages = total // 20
    return render_template("repost.html", result=result, pages=pages, page=page)

@app.route('/kaufuzys', methods=['GET'])
def kfzys():
    """
    资源搬运
    """
    return render_template("kuafuzys.html")

@app.route('/kaufuzys/start', methods=['GET'])
def kfzys_repost_extract():
    """
    资源搬运
    """
    page = request.args.get('page', type=int, default=1)
    uid = request.args.get('uid', type=str)
    if KuafuzysAcquisition.start(uid, page=page):
        return "成功"
    else:
        return "失败"

@app.route('/repost/pushKuaFu', methods=['GET'])
def push_kuafu():
    """
    资源搬运
    """
    # 获取请求参数
    id = request.args.get('id', type=int)
    quake_href = request.args.get('quake_href', type=str)
    print(f"夸父资源>>> 发布到论坛，id:{id},quake_href:{quake_href}")
    bbs_info = BBSInfo.get_byid(id)
    bbs_info.quake_new_href = quake_href
    # 替换内容中的网盘地址
    bbs_info.replace_content()
    kuafu = KuaFu(bbs_info)
    return kuafu.add_kuafu()



if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')