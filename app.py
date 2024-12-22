from flask import Flask, render_template, request
import logging

from api import FeiShu, SteamInfo

app = Flask(__name__)

# 配置日志
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

@app.route('/')
def home():  # put application's code here
    return render_template("index.html")

@app.route('/add_feishu_record', methods=['POST'])
def add_record():
    data = request.get_json()
    print(data)
    game_data = SteamInfo.get_game_data(data)
    app.logger.info(game_data)
    if FeiShu.add_record(game_data):
        return "添加成功"
    else:
        return "添加失败"


@app.route('/steam_name/<appID>', methods=['GET'])
def steam_name(appID):
    game_data = SteamInfo.fetch_steam_app_info(appID)
    # 如果 game_data 返回 None 或者没有 'title' 字段，需要进行处理
    if game_data and "title" in game_data:
        return game_data["title"]
    else:
        return "游戏名称未找到"

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')