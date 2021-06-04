
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
                
    if login_state == 0 or '重新填寫' in msg:
        sheet_id.update_cell(no, 2, str(1))
        message = TextSendMessage(text= '請輸入姓名 若超過1分鐘沒有回應請再次輸入')
        line_bot_api.reply_message(event.reply_token, message)

    if login_state == 1:
        student_num = int(sheet_name.cell(1,1).value)
        name = msg
        seatnum = ''
        _class = ''
        name_exist = False
        
        for i in range (1,student_num + 2):
                if sheet_name.cell(i,1).value == msg:
                    seatnum = sheet_name.cell(i,3).value
                    _class = sheet_name.cell(i,2).value
                    name_exist = True
                    break
                    
        if name_exist:
            sheet_id.update_cell(no, 2, str(2))
            sheet_id.update_cell(no, 3, _class)
            sheet_id.update_cell(no, 4, seatnum)
            sheet_id.update_cell(no, 5, name)
            sheet_id.update_cell(no, 6, '0')
            for i in range (7, 27):
                sheet_id.update_cell(no, i, '0')
            sheet_id.update_cell(no, 6, '0')
            message = TemplateSendMessage(
                alt_text='確認班級座號姓名？',
                template=ConfirmTemplate(
                    text="你是"+ _class + ' ' + seatnum + '號 ' + name + '嗎?',
                    actions=[
                        PostbackTemplateAction(
                            label="確認",
                            text="開始 Unit 3 聽力測驗 請點開影片檔案 並選出你聽到的單字 若超過30秒沒有出現題目 請複製對話中最後一條訊息並傳送 注意重複作答系統不予計分",
                            data="會員註冊"
                        ),
                        MessageTemplateAction(
                            label="重新填寫",
                            text="重新填寫"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            sheet_id.update_cell(no, 2, str(1))
            message = TextSendMessage(text= '查無此人 請重新輸入')
            line_bot_api.reply_message(event.reply_token, message)
            

    if '開始' in msg or '#0' in msg:
        message = VideoSendMessage(
            original_content_url='https://imgur.com/sGnmpiG.mp4', 
            preview_image_url='https://imgur.com/2CJYX6c.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'subjick', text = '#1 your ans : subjick\ncorrect ans : subject')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'subject', text = '#1 your ans : subject\ncorrect ans : subject\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'subjict', text = '#1 your ans : subjict\ncorrect ans : subject')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#1' in msg:
        if 'good job!' in msg and sheet_id.cell(no,7).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 7, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/ssC2YWd.mp4', 
            preview_image_url='https://imgur.com/4ARs5aO.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'favor', text = '#2 your ans : favor\ncorrect ans : favorite')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'favorite', text = '#2 your ans : favorite\ncorrect ans : favorite\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'faveret', text = '#2 your ans : faveret\ncorrect ans : favorite')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#2' in msg:
        if 'good job!' in msg and sheet_id.cell(no,8).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 8, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/RETJM3W.mp4', 
            preview_image_url='https://imgur.com/hZHDi6D.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'social studies', text = '#3 your ans : social studies\ncorrect ans : social studies\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'sosial studies', text = '#3 your ans : sosial studies\ncorrect ans : social studies')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'social studys', text = '#3 your ans : social studys\ncorrect ans : social studies')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    if '#3' in msg:
        if 'good job!' in msg and sheet_id.cell(no,9).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 9, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/k26ZoDJ.mp4', 
            preview_image_url='https://imgur.com/t7keRVy.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'musical', text = '#4 your ans : musical\ncorrect ans : music')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'muzic', text = '#4 your ans : muzic\ncorrect ans : music')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'music', text = '#4 your ans : music\ncorrect ans : music\ngood job!')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#4' in msg:
        if 'good job!' in msg and sheet_id.cell(no,10).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 10, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/YCVRCto.mp4', 
            preview_image_url='https://imgur.com/st821yg.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'mass', text = '#5 your ans : mass\ncorrect ans : math')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'mase', text = '#5 your ans : mase\ncorrect ans : math')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'math', text = '#5 your ans : math\ncorrect ans : math\ngood job!')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#5' in msg:
        if 'good job!' in msg and sheet_id.cell(no,11).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 11, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/mWrfDIu.mp4', 
            preview_image_url='https://imgur.com/tOUdChN.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'hir', text = '#6 your ans : hir\ncorrect ans : read books')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'her', text = '#6 your ans : her\ncorrect ans : her\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'fer', text = '#6 your ans : fer\ncorrect ans : her')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#6' in msg:
        if 'good job!' in msg and sheet_id.cell(no,12).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 12, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/9IGNXlX.mp4', 
            preview_image_url='https://imgur.com/7ezNT5R.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'noze', text = '#7 your ans : noze\ncorrect ans : noses')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'nose', text = '#7 your ans : nose\ncorrect ans : nose\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'nozzle', text = '#7 your ans : nozzle\ncorrect ans : nose')
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#7' in msg:
        if 'good job!' in msg and sheet_id.cell(no,13).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 13, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/C3wzZHC.mp4', 
            preview_image_url='https://imgur.com/BgRCXLX.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'boat', text = '#8 your ans : boat\ncorrect ans : boat\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'boot', text = '#8 your ans : boot\ncorrect ans : boat')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = "board", text = "#8 your ans : board\ncorrect ans : boat")
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#8' in msg:
        if 'good job!' in msg and sheet_id.cell(no,14).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 14, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/cM6Zsqz.mp4', 
            preview_image_url='https://imgur.com/fdgthsL.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'snooze', text = '#9 your ans : snooze\ncorrect ans : snow')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'snow', text = '#9 your ans : snow\ncorrect ans : snow\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = "snail", text = "#9 your ans : snail\ncorrect ans : snow")
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '#9' in msg:
        if 'good job!' in msg and sheet_id.cell(no,15).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 15, '1')
        message = VideoSendMessage(
            original_content_url='https://imgur.com/GboIgZG.mp4', 
            preview_image_url='https://imgur.com/qRmhPT1.png',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = MessageAction(label = 'show', text = '# 10 your ans : show\ncorrect ans : show\ngood job!')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = 'snow', text = '# 10 your ans : snow\ncorrect ans : show')
                    ),
                    QuickReplyButton(
                        action = MessageAction(label = "shoes", text = "# 10 your ans : shoes\ncorrect ans : show")
                    ),  
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)


    
    if '# 10' in msg:
        if 'good job!' in msg and sheet_id.cell(no,16).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 16, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 11',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/E4wtVGJ.png',
                title = "選擇填入空格的詞句",
                text = "What _____  your favorite subjects? ",
                actions=[
                    MessageTemplateAction(
                        label = 'is',
                        text = '# 11 your ans : is\ncorrect ans : are'
                    ),
                    MessageTemplateAction(
                        label = 'are',
                        text = '# 11 your ans : are\ncorrect ans : are\ngood job!'
                    ),
                    MessageTemplateAction(
                        label= 'do',
                        text = '# 11 your ans : do\ncorrect ans : are'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    
    if '# 11' in msg:
        if 'good job!' in msg and sheet_id.cell(no,17).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 17, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 12',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/Rp9LKBa.png',
                
                text = "My favorite ________ are science and math. ",
                actions=[
                    MessageTemplateAction(
                        label = 'subject',
                        text = '# 12 your ans : subject\ncorrect ans : subjects'
                    ),
                    MessageTemplateAction(
                        label = 'subjects',
                        text = '# 12 your ans : subjects\ncorrect ans : subjects\ngood job!'
                    ),
                    MessageTemplateAction(
                        label= 'book',
                        text = '# 12 your ans : book\ncorrect ans : subjects'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 12' in msg:
        if 'good job!' in msg and sheet_id.cell(no,18).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 18, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 13',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/vriIBqw.png',
                
                text = "______ favorite subject is music.",
                actions=[
                    MessageTemplateAction(
                        label = "tina's",
                        text = "# 13 your ans : tina's\ncorrect ans : Tina's"
                    ),
                    MessageTemplateAction(
                        label = 'Tina',
                        text = "# 13 your ans : Tina\ncorrect ans : Tina's"
                    ),
                    MessageTemplateAction(
                        label= "Tina's",
                        text = "# 13 your ans : Tina's\ncorrect ans : Tina's\ngood job!"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 13' in msg:
        if 'good job!' in msg and sheet_id.cell(no,19).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 19, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 14',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/2ktphE6.png',
                title = "A:What is Jack's favorite subject? ",
                text = "B: ______ favorite subject is PE.",
                actions=[
                    MessageTemplateAction(
                        label = 'My',
                        text = '# 14 your ans : My\ncorrect ans : His'
                    ),
                    MessageTemplateAction(
                        label = 'Your',
                        text = '# 14 your ans : Your\ncorrect ans : His'
                    ),
                    MessageTemplateAction(
                        label= 'His',
                        text = '# 14 your ans : His\ncorrect ans : His\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 14' in msg:
        if 'good job!' in msg and sheet_id.cell(no,20).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 20, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 15',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/NSYMEMS.png',
                title = "A:What's the dog's favorite food? ",
                text = "B: ______ favorite food is meat.",
                actions=[
                    MessageTemplateAction(
                        label = 'Her',
                        text = '# 15 your ans : Her\ncorrect ans : Its'
                    ),
                    MessageTemplateAction(
                        label = 'His',
                        text = '# 15 your ans : His\ncorrect ans : Its'
                    ),
                    MessageTemplateAction(
                        label= 'Its',
                        text = '# 15 your ans : Its\ncorrect ans : Its\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    
    if '# 15' in msg:
        if 'good job!' in msg and sheet_id.cell(no,21).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 21, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 16',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/9ksK0is.png',
                title = "A:What is Mom's favorite food? ",
                text = "B: ______ favorite food is pizza.",
                actions=[
                    MessageTemplateAction(
                        label = "Mom's",
                        text = "# 16 your ans : Mom's\ncorrect ans : Her"
                    ),
                    MessageTemplateAction(
                        label = 'Her',
                        text = '# 16 your ans : Her\ncorrect ans : Her\ngood job!'
                    ),
                    MessageTemplateAction(
                        label= 'My',
                        text = '# 16 your ans : My\ncorrect ans : Her'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 16' in msg:
        if 'good job!' in msg and sheet_id.cell(no,22).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 22, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 17',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/Y1vvXux.png',
                title = "A: Is  your favorite subject Chinese ? ",
                text = "B:No, _______.",
                actions=[
                    MessageTemplateAction(
                        label = "I'm not",
                        text = "# 17 your ans : I'm not\ncorrect ans : it isn't"
                    ),
                    MessageTemplateAction(
                        label = 'it is',
                        text = "# 17 your ans : it is\ncorrect ans : it isn't"
                    ),
                    MessageTemplateAction(
                        label= "it isn't",
                        text = "# 17 your ans : it isn't\ncorrect ans : it isn't\ngood job!"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 17' in msg:
        if 'good job!' in msg and sheet_id.cell(no,23).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 23, '1')
        sheet_id.update_cell(no, 23, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 18',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/SJoGeQT.png',
                
                text = "Uh-oh! The magic light doesn't _______.",
                actions=[
                    MessageTemplateAction(
                        label = 'work',
                        text = '# 18 your ans : work\ncorrect ans : work\ngood job!'
                    ),
                    MessageTemplateAction(
                        label = 'works',
                        text = '# 18 your ans : works\ncorrect ans : work'
                    ),
                    MessageTemplateAction(
                        label= 'walk',
                        text = '# 18 your ans : walk\ncorrect ans : work'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 18' in msg:
        if 'good job!' in msg and sheet_id.cell(no,24).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 24, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 19',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/JQZd2b9.png',
                
                text = "No one can help you. ________ the music!",
                actions=[
                    MessageTemplateAction(
                        label = 'Listen to',
                        text = '# 19 your ans : Listen to\ncorrect ans : Face'
                    ),
                    MessageTemplateAction(
                        label = 'Head',
                        text = '# 19 your ans : Head\ncorrect ans : Face'
                    ),
                    MessageTemplateAction(
                        label= 'Face',
                        text = '# 19 your ans : Face\ncorrect ans : Face\ngood job!'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 19' in msg:
        if 'good job!' in msg and sheet_id.cell(no,25).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 25, '1')
        message = TemplateSendMessage(
            alt_text = 'Problem 20',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/goWtiMu.png',
                
                text = "I _____ ____ idea! Let's go to Madame Curie.",
                actions=[
                    MessageTemplateAction(
                        label = "think a",
                        text = "# 20 your ans : think a\ncorrect ans : have an"
                    ),
                    MessageTemplateAction(
                        label = "have a",
                        text = "# 20 your ans : have a\ncorrect ans : have an"
                    ),
                    MessageTemplateAction(
                        label = "have an",
                        text = "# 20 your ans : have an\ncorrect ans : have an\ngood job!"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    if '# 20' in msg:
        if 'good job!' in msg and sheet_id.cell(no,26).value == '0':
            score = str(int(sheet_id.cell(no,6).value) + 5)
            sheet_id.update_cell(no, 6, score)
        if 'ans' in msg:
            sheet_id.update_cell(no, 26, '1')
        message = TemplateSendMessage(
            alt_text = 'finished!',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/k1jt05e.png',
                title = "作答完成",
                text = "你的分數" + sheet_id.cell(no,6).value,
                actions=[
                    MessageTemplateAction(
                        label = "我知道了!",
                        text = "完成作答"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
       
    if '@' in msg:
        current = 0
        tag = ''
        for i in range (7, 27):
            if sheet_id.cell(no,i).value == '0':
                current = i-6
                break
        if current < 11:
            tag = '#' + str(current)
        else:
            tag = '# ' + str(current)
        message = TemplateSendMessage(
            alt_text = 'Error message',
            template=ButtonsTemplate(
                thumbnail_image_url = 'https://imgur.com/ZBnMXWf.png',
                title = "Sorry",
                text = "系統有些延遲",
                actions=[
                    MessageTemplateAction(
                        label = "重新載入",
                        text = tag
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

            

    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
