
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import tempfile, os
import datetime
import time
import traceback
#======python的函數庫==========

import gspread
from oauth2client.service_account import ServiceAccountCredentials



scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)

client = gspread.authorize(creds)
sheet = client.open("English_test")
sheet_problem = sheet.get_worksheet(0)
sheet_option = sheet.get_worksheet(1)
sheet_id = sheet.get_worksheet(2)
sheet_name = sheet.get_worksheet(3)

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi('TOi303gvTtC4ncGBIaUJmSLDvjRZrnbzpBuAr1f2SMh8WtjIXmTzFH1ALHzqpNruGPYT+c2KGNbIeDM5Hzn9fjR5m3ql1wvyFGPNk956PuA9U3HmcInqabuiPpxwRX/77UiN2iiF2aRZ2cKEg9LREwdB04t89/1O/w1cDnyilFU=')

# Channel Secret
handler = WebhookHandler('57853dccc508c4b194e42454586e9969')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
@static_vars(counter=0)
def handle_message(event):
    

    msg = event.message.text
    user_id = event.source.user_id
    total_num = int(sheet_id.cell(100,1).value)
    registered = False
    no = 0
    login_state = 0

    #check registration state
    if total_num != 0:
        for i in range(1,total_num + 1):
            if sheet_id.cell(i,1).value == user_id:
                no = i
                registered = True

    if not registered:
        no = total_num + 1
        sheet_id.update_cell(no, 1, user_id)
        sheet_id.update_cell(no, 2, str(0))
        sheet_id.update_cell(100, 1, str(no))
        registered = True

    login_state = int(sheet_id.cell(no,2).value)
    # 0:id reg / 1:name in / 2:name confirm / 3:start
                
    if login_state == 0:
        sheet_id.update_cell(no, 2, str(1))
        message = TextSendMessage(text= '請輸入姓名')
        line_bot_api.reply_message(event.reply_token, message)

    if login_state == 1:
        sheet_id.update_cell(no, 2, str(2))
        student_num = int(sheet_name.cell(1,1).value)
        name = msg
        seatnum = ''
        _class = ''
        name_exist = False
        
        for i in range (1,student_num + 1):
                if sheet_name.cell(i,1).value == msg:
                    seatnum = sheet_name.cell(i,3).value
                    _class = sheet_name.cell(i,2).value
                    name_exist = True
        '''
    elif log_in_state == 1:
        name = msg
        message = TextSendMessage(text= 'hello')
        
        message = TemplateSendMessage(
            alt_text='姓名確認',
            template=ConfirmTemplate(
                text='請確認 你是' + name + '嗎',
                actions=[
                    PostbackTemplateAction(
                        label="是的",
                        text="開始測驗",
                    ),
                    MessageTemplateAction(
                        label="重新輸入",
                        text="開始註冊"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
        log_in_state = 2
    #elif log_in_state == 2:
        
        
    
    
    
    if 'check last ID-CARD location' in msg:
        row = int(sheet_loc.cell(2,7).value) + 1 
        
        sim_lon = int(sheet_loc.cell(row,2).value) + 0.00000000000001 * int(sheet_loc.cell(row,3).value)
        sim_lat = int(sheet_loc.cell(row,4).value) + 0.00000000000001 * int(sheet_loc.cell(row,5).value)
        
        sim_lon = int(sheet_loc.cell(100,2).value) + 0.00000000000001 * int(sheet_loc.cell(100,3).value)
        sim_lat = int(sheet_loc.cell(100,4).value) + 0.00000000000001 * int(sheet_loc.cell(100,5).value)
        message = LocationSendMessage(
            title='previous location',
            address='上一次拿出卡片的位置',
            latitude = sim_lat,
            longitude = sim_lon
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif 'check present wallet location' in msg:
        
        sim_lon = int(sheet_wal.cell(2,2).value) + 0.00000000000001 * int(sheet_wal.cell(2,3).value)
        sim_lat = int(sheet_wal.cell(2,4).value) + 0.00000000000001 * int(sheet_wal.cell(2,5).value)
        
        sim_lon = int(sheet_wal.cell(100,2).value) + 0.00000000000001 * int(sheet_wal.cell(100,3).value)
        sim_lat = int(sheet_wal.cell(100,4).value) + 0.00000000000001 * int(sheet_wal.cell(100,5).value)
        message = LocationSendMessage(
            title='walltet location',
            address='錢包的現在位置',
            latitude = sim_lat,
            longitude = sim_lon
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif 'check cost info' in msg:
        
        text = ''
        for i in range(1,7,1):
            text += sheet_cost.cell(i,7).value
            text += sheet_cost.cell(i,8).value
            text += '\n'
            message = TextSendMessage(text)
        
        message = Carousel_Template_cost()
        line_bot_api.reply_message(event.reply_token, message)
    elif 'off' in msg:
        message = TextSendMessage(text= 'light is turned off')
        line_bot_api.reply_message(event.reply_token, message)
        sheet_light.update_cell(1, 1, str(0))
    elif 'set wallet password' in msg:
        message = TextSendMessage(text= 'please enter your "auth" + your 4 digit "new password"')
        line_bot_api.reply_message(event.reply_token, message)
    elif 'auth' in msg:
        password = ''
        for i in range (4,8,1):
            password += msg[i]
        sheet_pass.update_cell(1, 1, password)
        message = TextSendMessage(text= 'password is set to ' + password)
        line_bot_api.reply_message(event.reply_token, message)
    elif 'turn on signal light' in msg:
        message = Carousel_Template_off()
        line_bot_api.reply_message(event.reply_token, message)
        sheet_light.update_cell(1, 1, str(1))
    else:
        message = Carousel_Template_menu()
        line_bot_api.reply_message(event.reply_token, message)
        
        '''
    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
