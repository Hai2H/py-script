from flask import Flask, render_template, request
import logging

from api import FeiShu, SteamInfo

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')