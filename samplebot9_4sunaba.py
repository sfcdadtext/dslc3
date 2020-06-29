#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time
import random
import requests
import json

### telegram
# アクセストークン
TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"

### sunaba
# BOTID
BOTID = "YYYYYYYYYY"
# 最初のTopicId
TopicId = "ZZZZZZZZZZ"

# 1対話の長さ(ユーザの発話回数)．ここは固定とする
DIALOGUE_LENGTH = 15

"""SUNABAで作成したボットと接続するTelegramボット"""

# 対話履歴を受け取り，応答を返す．
# ここを各自書き換えれば自分のシステムができる
def reply(user_utterance, count, appid):
    # リクエストURL(dialogue)
    url = "https://api-sunaba.xaiml.docomo-dialog.com/dialogue"
    # initTalkingFlagの有無
    if count == 1:
        # リクエスト
        payload = {
          "appId": appid,
          "botId": BOTID,
          "voiceText": user_utterance,
          "language": "ja-JP",
          "initTalkingFlag": "true",
          "initTopicId": TopicId
        }
    else:
        # リクエスト
        payload = {
          "appId": appid,
          "botId": BOTID,
          "voiceText": user_utterance,
          "language": "ja-JP",
          "initTalkingFlag": "false"
        }
    headers = {'Content-type': 'application/json;charset=UTF-8'}
    # リクエスト送信
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    data = r.json()

    return data['systemText']["expression"]


class SampleBot:
    def __init__(self):
        self.user_context = {}

    def start(self, bot, update):
        # リクエストURL(registration)
        url = "https://api-sunaba.xaiml.docomo-dialog.com/registration"
        # リクエスト
        payload = {
          "botId":BOTID,
          "appKind": "sunaba",
          "notification" : "false"
        }
        headers = {'Content-type': 'application/json;charset=UTF-8'}
        # リクエスト送信
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        data = r.json()

        # 対話ログと発話回数を初期化
        self.user_context[update.message.from_user.id] = {"context": [], "count": 0, "appid": data['app_id']}

    def message(self, bot, update):
        if update.message.from_user.id not in self.user_context:
            self.user_context[update.message.from_user.id] = {"context": [], "count": 0}

        # ユーザ発話の回数を更新
        self.user_context[update.message.from_user.id]["count"] += 1

        # ユーザ発話をcontextに追加
        self.user_context[update.message.from_user.id]["context"].append(update.message.text)

        # replyメソッドによりcontextから発話を生成
        send_message = reply(update.message.text, self.user_context[update.message.from_user.id]["count"], self.user_context[update.message.from_user.id]["appid"])

        # 送信する発話をcontextに追加
        self.user_context[update.message.from_user.id]["context"].append(send_message)

        # 発話を送信
        update.message.reply_text(send_message)

        if self.user_context[update.message.from_user.id]["count"] >= DIALOGUE_LENGTH:
            # 対話IDは unixtime:user_id:bot_username
            unique_id = str(int(time.mktime(update.message["date"].timetuple()))) + u":" + str(update.message.from_user.id) + u":" + bot.username

            update.message.reply_text(u"_FINISHED_:" + unique_id)
            update.message.reply_text(u"対話終了です．エクスポートした「messages.html」ファイルを，フォームからアップロードしてください．")


    def run(self):
        updater = Updater(TOKEN)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", self.start))

        dp.add_handler(MessageHandler(Filters.text, self.message))

        updater.start_polling()

        updater.idle()


if __name__ == '__main__':
    mybot = SampleBot()
    mybot.run()
