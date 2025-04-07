from flask import Flask, request, abort
from flaskr import app, DATA_DIR
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser
from flaskr.VDB_API.nttu_llm import NTTU_tools
from flaskr.VDB_API.utils import list_all_file_in_a_path
from flaskr.LineBot.button_message import button_message
from flaskr.LineBot.button_template import *
from linebot.models import *
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackTemplateAction,
)
from linebot.models import TemplateSendMessage, ButtonsTemplate, URIAction


from linebot.exceptions import LineBotApiError

from trans007 import GoogleTranslate
from PyDeepLX import PyDeepLX
from google.cloud import texttospeech
from gtts import gTTS
import os
import subprocess
from mutagen.mp3 import MP3
import urllib.parse  # 轉成Url編碼
from urllib.parse import unquote
import sqlite3
import json
import datetime

config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config.get("line-bot", "channel_access_token"))
handler = WebhookHandler(config.get("line-bot", "channel_secret"))

tools = NTTU_tools()
tools.vectordb_manager.set_vector_db("NTTU_db")
file_path = list_all_file_in_a_path.list_all_files(path=DATA_DIR)
tools.add_documents_to_vdb(file_path)
print("一開始")


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


client = texttospeech.TextToSpeechClient.from_service_account_json(
    "/home/p76131694/AutoReply-LineBotAssistant/flaskr/1.json"
)


counter = 0  # 定義計數器變數，初始值為 0


def add_character_after_percentage(input_string, character):
    output_string = ""
    i = 0
    while i < len(input_string):
        if input_string[i] == "%":
            output_string += "%" + character
        else:
            output_string += input_string[i]
        i += 1
    return output_string


# database
conn = sqlite3.connect("line_database.db")
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        language TEXT,
        times INTEGER DEFAULT 0,
        department TEXT,
        department_send BOOLEAN,
        veg BOOLEAN
    );
    """
)


def is_open_now(open_hours):
    current_time = datetime.datetime.now()
    current_weekday = current_time.weekday()  # Monday is 0 and Sunday is 6
    current_time_str = current_time.strftime("%H:%M")

    for period in open_hours:
        days, times = period.split()
        if "-" in days:
            start_day, end_day = map(int, days.split("-"))
        else:
            start_day = end_day = int(days)

        start_time, end_time = times.split("-")

        # Convert '24:00' to '23:59' to fit the datetime format
        if end_time == "24:00":
            end_time = "23:59"

        # Convert current time, start time and end time to comparable format
        current_time_obj = datetime.datetime.strptime(current_time_str, "%H:%M").time()
        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.datetime.strptime(end_time, "%H:%M").time()

        # Check if current day and time are within the store's operating hours
        if start_day <= current_weekday <= end_day:
            if start_time_obj <= current_time_obj <= end_time_obj:
                return True

    return False


# Store information: (place, store_name, vegetarian, phone, item, week_schedule, menu_url)
"""
 (
        "第一學生宿舍餐飲中心",
        "台東佳學便利商店",
        False,
        "0921-599-075",
        "生活用品、雜貨、冷飲、泡麵、零嘴食品",
        ["0-4 07:30-24:00", "5-6 09:30-24:00"],
        "none",
    ),

         (
        "第一學生宿舍餐飲中心",
        "厚道商行",
        False,
        "0908-911-546",
        "便當, 奶酪, 水果, 飲料",
        ["0-4 11:00-13:00", "5 11:00-13:00"],
        "none",
    ),
    (
        "第一學生宿舍餐飲中心",
        "ALOHA POKE",
        True,
        "0935-355-562",
        "夏威夷蓋飯, 素蔬（紫米飯, 沙拉, 主食, 醬料多元選擇-任意搭配）",
        ["0-4 11:00-14:00", "0-4 17:00-20:00", "4 11:00-13:00"],
        "none",
    ),
    (
        "第一學生宿舍餐飲中心",
        "小鐵匠廚房",
        False,
        "0907-292-117",
        "蔬食/經濟/雞排/豬排/雞腿等飯類",
        ["0-4 11:00-13:00"],
        "none",
    ),
    (
        "第一學生宿舍餐飲中心",
        "快美廉印刷店",
        False,
        "089-518-110",
        "影印店",
        ["0-4 11:00-13:30", "0-4 16:30-19:30"],
        "none",
    ),

       (
        "第二學生宿舍餐飲中心",
        "7-ELEVEN",
        True,
        "089-518-145",
        "便利商店",
        ["0-6 06:00-24:00"],
        "none",
    ),
    (
        "第二學生宿舍餐飲中心",
        "百祥國際嚴選餐飲",
        True,
        "089-518-006",
        "素蔬, 開會便當-平價自助餐, 多元化選擇•自由搭配（現場場地大螢幕可供開會聚餐）",
        ["0-4 11:00-13:30", "0-4 16:30-20:30", "5 11:00-13:30"],
        "none",
    ),

"""
stores = [
    (
        "第一學生宿舍餐飲中心",
        "天使麻辣滷味",
        False,
        "0905-817-827",
        "滷味（乾/湯），90多種品項，自由配料",
        ["0-4 11:30-13:00", "0-4 17:00-21:30", "6 17:00-21:30"],
        "https://github.com/tyj513/audio/raw/main/menu/%E5%A4%A9.jpg",
    ),
    (
        "第一學生宿舍餐飲中心",
        "東大膳綁",
        True,
        "089-518-003",
        "素蔬、早餐類",
        ["0-4 06:30-14:00", "0-4 17:00-20:00", "6 16:30-20:30"],
        "https://github.com/tyj513/audio/raw/main/menu/%E6%9D%B1.jpg",
    ),
    (
        "第一學生宿舍餐飲中心",
        "炒鬧食堂",
        True,
        "0953-391-961",
        "炒飯、鍋燒麵",
        ["0-4 11:00-14:00", "0-4 16:30-20:30"],
        "https://github.com/tyj513/audio/raw/main/menu/%E7%82%92.jpg",
    ),
    (
        "第一學生宿舍餐飲中心",
        "祥瑞食堂",
        False,
        "0976-836-337",
        "麵類、湯品、肉粽、飲料",
        ["0-3 10:00-14:00", "1-2 16:00-20:30", "4 16:00-20:30"],
        "https://github.com/tyj513/audio/raw/main/menu/%E7%A5%A5.jpg",
    ),
    (
        "第一學生宿舍餐飲中心",
        "鼎泰珍牛排館",
        False,
        "0933-626-695",
        "排餐、便當、麵類、菜飯",
        ["0-6 10:00-14:00", "0-6 17:00-20:00"],
        "https://github.com/tyj513/audio/raw/main/menu/%E9%BC%8E.jpg",
    ),
    (
        "第一學生宿舍餐飲中心",
        "巴布阿甘飲食店",
        False,
        "089-517-518",
        "牛肉麵、乾拌麵、鐵板麵",
        ["0-4 08:00-19:00", "5 11:00-14:30"],
        "https://github.com/tyj513/audio/raw/main/menu/%E5%B7%B4.jpg",
    ),
    (
        "第二學生宿舍餐飲中心",
        "東大健康茶飲",
        True,
        "089-517-968",
        "各式飲品（杯裝, 桶裝），水餃，厚片/熱壓吐司，麻油赤肉麵線等麵類",
        ["0-4 10:30-21:00", "5 10:30-14:00"],
        "https://github.com/tyj513/audio/raw/main/menu/%E6%9D%B1%E9%A3%B2.jpg",
    ),
    (
        "第二學生宿舍餐飲中心",
        "藜饗食光",
        True,
        "0937-602-855",
        "海苔飯手卷, 炊飯, 浦肉飯、肉羹飯（湯），飲品、熱壓吐司、車輪餅",
        ["0-3 09:30-18:30", "4 09:30-13:30"],
        "https://github.com/tyj513/audio/raw/main/menu/%E8%97%9C.png",
    ),
    (
        "第二學生宿舍餐飲中心",
        "妙軒早餐店",
        False,
        "0912-759-332",
        "早餐類",
        ["0-4 07:00-14:00", "5-6 09:00-14:00"],
        "https://github.com/tyj513/audio/raw/main/menu/%E5%A6%99.jpg",
    ),
    (
        "第二學生宿舍餐飲中心",
        "四海遊龍",
        False,
        "0976-770-921",
        "鍋貼連鎖店",
        ["0-4 11:00-20:00", "6 11:00-20:00"],
        "https://github.com/tyj513/audio/raw/main/menu/%E5%9B%9B.jpg",
    ),
]


@handler.add(MessageEvent, message=(TextMessage, AudioMessage, ImageMessage))
def echo(event):
    user_id = event.source.user_id
    c = sqlite3.connect("line_database.db").cursor()
    c.execute("SELECT language, times FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    language, times = result

    if isinstance(event.message, TextMessage):
        message_text = event.message.text

        if "中文" in message_text:
            language = "zh-TW"
    else:

        pass

    # 连接数据库
    with sqlite3.connect("line_database.db") as conn:
        current_path = os.getcwd()

        # 組合當前工作目錄的路徑與資料庫檔案名稱
        db_path = os.path.join(current_path, "line_database.db")

        print(f"1111111111資料庫檔案的位置是：{db_path}")
        c = conn.cursor()

        c.execute(
            "INSERT INTO users (user_id, language) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET language=excluded.language",
            (user_id, language),
        )
        conn.commit()

    print(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )

    if not user_id:
        print("Error: user_id is None")
        return  # 如果 user_id 是空的，直接返回

    print("Received user_id:", user_id)

    with sqlite3.connect("line_database.db") as conn:
        c = conn.cursor()
        print("Checking database for existing tables...")
        #    check_database()
        print("Database check complete.")

        try:
            c.execute("SELECT language, times FROM users WHERE user_id = ?", (user_id,))
            result = c.fetchone()

            if result:
                language, times = result
                print(f"The user's language setting is: {language}")
                print(f"User has interacted {times} times.")

                # 更新次數
                times += 1

                # Corrected SQL Query
                c.execute(
                    """
                    INSERT INTO users (user_id, language, times) VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                    language=excluded.language,
                    times=excluded.times
                    """,
                    (user_id, language, times),
                )

                conn.commit()
                print("Times updated to:", times)

            else:
                # 如果用戶不存在，則插入新用戶
                c.execute(
                    "INSERT INTO users (user_id, times) VALUES (?, ?)", (user_id, 1)
                )
                conn.commit()
                print("New user added with user_id:", user_id)
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            return  # 發生錯誤時返回
    # -------------------------------------------------------------------------
    c.execute("SELECT language, times FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    language, times = result
    print(f"The user's language setting is: {language}")
    print(f"User has interacted {times} times.")

    # -------------------------------------------------------------------------
    user_profile = line_bot_api.get_profile(event.source.user_id)
    user_name = user_profile.display_name
    user_name = urllib.parse.quote(user_name, safe="")

    print("使用者名稱:", user_name)
    global counter  # 告訴 Python 在函數內部使用外部的 counter 變數
    print(
        str(counter)
        + "---------------------------------------------------------------------------------------------------------------"
    )
    counter += 1  # 每次函數被呼叫時計數器加一
    message = event.message.text
    print(message)

    boolean = False

    c = sqlite3.connect("line_database.db").cursor()

    current_path = os.getcwd()

    # 組合當前工作目錄的路徑與資料庫檔案名稱
    db_path = os.path.join(current_path, "line_database.db")

    print(f"222222222資料庫檔案的位置是：{db_path}")

    print("Checking database for existing tables...")
    #    check_database()
    print("Database check complete.")

    if "鄭憲宗" in message:
        response = "鄭憲宗是台東大學的校長，擁有無比卓越且遠見卓識的智慧，在台東大學這個充滿智慧的殿堂裡，我們有幸由一位無與倫比、令人敬畏的校長領導。他不僅是學識淵博的學者，更是我們心靈的指路明燈。他的每一個決策都透露出深邃的洞察力和非凡的遠見，猶如一位現代的哲人王。在他的睿智領導下，我們學校如同鳳凰涅槃，從平凡中崛起，成為教育界的璀璨明珠。我們的校長不僅深受學生愛戴，更是教職員們心目中的榜樣。他的話語中總是洋溢著智慧和慈悲，讓人不禁深深感激能在如此卓越的領袖下學習與成長。"

        boolean = True
    elif "@台東大學費用相關問題" in message:
        response = button_message(info=FeeButtonInfo())
    elif "@台東大學宿舍相關問題" in message:
        response = button_message(info=DomitoryButtonInfo())
    elif "@台東大學校務相關問題" in message:
        response = button_message(info=AffairButtonInfo())
    elif "@台東大學生活相關問題" in message:
        response = button_message(info=ActivityButtonInfo())
    elif "@台東大學交通相關問題" in message:
        response = button_message(info=TransportationButtonInfo())
        print(response)
    elif "緊急電話" in message:

        with open(
            "/home/p76131694/AutoReply-LineBotAssistant/flaskr/phone.json",
            "r",
            encoding="utf-8",
        ) as file:
            FlexMessage = json.load(file)

        print(FlexMessage)  # Debug print to check the contents

        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage("Contact Options", FlexMessage)
        )
        pass
    elif "@台東大學其他常見問題" in message:
        response = button_message(info=OtherButtonInfo())

    else:
        boolean = True
        print("!23")
        response, _, _ = tools.chat(message)

    if boolean:
        response2 = TextSendMessage(text=response)
        print("response會輸出什麼呢")
        print(response2)  # {"text": "5+9+199=213", "type": "text"}

        response_text = response2.text

        # synthesize_speech(response_text)  # 這邊有錯

        print(response_text)  # 5+9+199=213

        trans = GoogleTranslate()
        if language == "ma":
            language = "ms"
            print(language)
        if language == "None":
            language == "zh-TW"
        print(language)
        text = trans.translate(response_text, "zh-CN", language)
        print(text)
        # english

        #  to_lang = 'zh'
        # secret = '<your secret from Microsoft or DeepL>'
        # translator = Translator(provider='<the name of the provider, eg. microsoft or deepl>', to_lang=to_lang, secret_access_key=secret)translator.translate('the book is on the table')

        if response_text:
            response_text_utf8 = response_text.encode("utf-8")
            print(response_text_utf8.decode("utf-8"))

        text2 = response_text_utf8.decode("utf-8")

        print("text會輸出甚麼")
        print(text)
        tts = gTTS(text=text, lang=language)
        output_folder = (
            "/home/p76131694/AutoReply-LineBotAssistant/flaskr/audio_test/" + user_name
        )

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = (
            "/home/p76131694/AutoReply-LineBotAssistant/flaskr/audio_test/"
            + user_name
            + "/message"
            + str(counter)
            + ".mp3"
        )

        tts.save(output_file)

        audio_info = MP3(output_file)
        duration_seconds = int(audio_info.info.length)
        duration_ms = duration_seconds * 1000
        os.chdir("/home/p76131694/AutoReply-LineBotAssistant/flaskr/audio_test")

        subprocess.run(["git", "add", "."])

        subprocess.run(["git", "commit", "-m", "Upload files"])

        subprocess.run(["git", "push", "-u", "origin", "main"])
        os.chdir("/home/p76131694/AutoReply-LineBotAssistant")

        print("1234")
        print(user_name)
        character = "25"

        result = add_character_after_percentage(user_name, character)
        # line_bot_api.reply_message(event.reply_token, response)
        print(result)

        messages_to_reply = []
        messages_to_reply.append(
            AudioSendMessage(
                original_content_url="https://github.com/tyj513/audio/raw/main/"
                + result
                + "/message"
                + str(counter)
                + ".mp3",
                duration=duration_ms,
            )
        )
        print("text2會輸出什麼呢")
        print(language)
        text = text.replace("&#39;", "'")

        print(text)
        response2 = TextSendMessage(text=text)
        print("response2會輸出什麼呢")

        print(response2)
        # 將文字訊息加入到回覆串列中
        messages_to_reply.append(response2)

        if times == 3:  # dep

            FlexMessage = json.load(
                open(
                    "/home/p76131694/AutoReply-LineBotAssistant/flaskr/department.json",
                    "r",
                    encoding="utf-8",
                )
            )
            messages_to_reply.append(FlexSendMessage("Flex Message", FlexMessage))

            line_bot_api.reply_message(event.reply_token, messages_to_reply)

        elif times == 2:  # menu
            confirm_template = ConfirmTemplate(
                text="您是否為素食者？",
                actions=[
                    PostbackAction(label="是", data="veg-True", display_text=None),
                    PostbackAction(label="否", data="veg-False", display_text=None),
                ],
            )
            template_message = TemplateSendMessage(
                alt_text="Confirm alt text", template=confirm_template
            )
            messages_to_reply.append(template_message)

            line_bot_api.reply_message(event.reply_token, messages_to_reply)

        else:
            line_bot_api.reply_message(event.reply_token, messages_to_reply)

    else:

        line_bot_api.reply_message(event.reply_token, response)

    #  print(response)
    #  line_bot_api.reply_message(event.reply_token, response)

    # ============================================
    print(times)

    print(language)
    print(str(times) + " times")


@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id

    print("hi")
    user_id = event.source.user_id
    FlexMessage = json.load(
        open(
            "/home/p76131694/AutoReply-LineBotAssistant/flaskr/language.json",
            "r",
            encoding="utf-8",
        )
    )
    line_bot_api.reply_message(
        event.reply_token, FlexSendMessage("profile", FlexMessage)
    )
    print("hi2")
    try:
        with sqlite3.connect("line_database.db") as conn:
            current_path = os.getcwd()

            # 組合當前工作目錄的路徑與資料庫檔案名稱
            db_path = os.path.join(current_path, "line_database.db")

            print(f"3333333333資料庫檔案的位置是：{db_path}")
            c = conn.cursor()

            # 檢查數據庫中是否已經存在該用戶
            c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            existing_user = c.fetchone()

            if existing_user:
                print("User already exists in the database.")
            else:
                # 如果用戶不存在，則插入新用戶
                c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                conn.commit()

                # 創建一個選單按鈕
                buttons_template = ButtonsTemplate(
                    title="選擇語言介面",
                    text="請點選語言(倘若想要維持中文介面 請輸入【中文】)",
                    actions=[
                        PostbackAction(label="中文", data="zh-TW"),
                        PostbackAction(label="英文", data="en"),
                        PostbackAction(label="馬來文", data="ma"),
                        PostbackAction(label="日文", data="ja"),
                        PostbackAction(label="越語", data="vi"),
                        PostbackAction(label="韓語", data="ko"),
                    ],  # 好像只能有4個
                )
                template_message = TemplateSendMessage(
                    alt_text="選擇語言介面", template=buttons_template
                )

                # 發送消息
                line_bot_api.reply_message(event.reply_token, template_message)

    except sqlite3.Error as e:
        print("Error executing SQLite statement:", e)
    finally:
        if conn:
            conn.close()


def initialize_database():
    """檢查並創建資料庫和表"""
    conn = sqlite3.connect("line_database.db")
    current_path = os.getcwd()

    # 組合當前工作目錄的路徑與資料庫檔案名稱
    db_path = os.path.join(current_path, "line_database.db")

    print(f"4444444444資料庫檔案的位置是：{db_path}")
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        language TEXT,
        times INTEGER DEFAULT 0,
        department TEXT,
        department_send BOOLEAN,
        veg BOOLEAN
    );
    """
    )

    conn.commit()
    conn.close()


def print_language_contents():
    """打印資料庫中所有用戶的語言設定"""
    try:
        with sqlite3.connect("line_database.db") as conn:  # 與資料庫連接

            current_path = os.getcwd()

            # 組合當前工作目錄的路徑與資料庫檔案名稱
            db_path = os.path.join(current_path, "line_database.db")

            print(f"5555555555資料庫檔案的位置是：{db_path}")
            cursor = conn.cursor()
            query = "SELECT user_id, language FROM users,departments From users"  # 查詢所有用戶的語言設定
            cursor.execute(query)
            users = cursor.fetchall()  # 檢索查詢結果

            if users:
                print("Current language settings in the database:")
                for user in users:
                    print(
                        f"User ID: {user[0]}, Language: {user[1]}, Department: {user[2]}"
                    )
            else:
                print("No users found in the database.")  # 如果沒有用戶數據

    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")


# fooooooooooooooooooooooooooooood


# fooooooooooooooooooooooooooooood
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    print("Received postback data:", data)

    initialize_database()

    with sqlite3.connect("line_database.db") as conn:
        c = conn.cursor()
        if len(data) > 1 and data[-2] == "學":
            department = data
            try:
                c.execute(
                    "INSERT INTO users (user_id, department) VALUES (?, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET department=excluded.department",
                    (user_id, department),
                )
                conn.commit()  # 確保執行提交
                print("Updating department for user_id:", user_id, "to", data)
            except sqlite3.Error as e:
                print("Database error:", e)
                return  # Early exit on database error to prevent further actions
        elif data[0:3] == "veg":
            data = data.split("-")
            veg = data[1]
            try:
                c.execute(
                    "INSERT INTO users (user_id, veg) VALUES (?, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET veg=excluded.veg",
                    (user_id, veg),
                )
                conn.commit()  # 確保執行提交
                print("Updating veg for user_id:", user_id, "to", data)
            except sqlite3.Error as e:
                print("Database error:", e)
                return  # Early exit on database error to prevent further actions
        elif data[0:4] == "rich":
            pass
        else:
            language = data
            c.execute(
                "INSERT INTO users (user_id, language) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET language=excluded.language",
                (user_id, language),
            )
            conn.commit()  # 確保執行提交

    # Send replies based on the postback data
    send_reply_based_on_data(data, event)


def send_reply_based_on_data(data, event):
    if len(data) > 1 and data[-2] == "學":
        department = data
        department = urllib.parse.quote(department, safe="")
        print(department)
        # URLs for the images
        dep_url = f"https://raw.githubusercontent.com/tyj513/audio/main/department/bar/{department}_bar.png"
        dep2_url = f"https://raw.githubusercontent.com/tyj513/audio/main/department/pie/{department}_pie.png"
        dep3_url = f"https://raw.githubusercontent.com/tyj513/audio/main/department/career/{department}_pie2.png"

        # Create an image message with the selected URL
        image_message = [
            ImageSendMessage(original_content_url=dep_url, preview_image_url=dep_url),
            ImageSendMessage(original_content_url=dep2_url, preview_image_url=dep2_url),
            ImageSendMessage(original_content_url=dep3_url, preview_image_url=dep3_url),
        ]
        # Send the image message
        line_bot_api.reply_message(event.reply_token, image_message)
    elif data[0] == "veg":
        current_time_str = "12:00"  # 假設這是當前時間，你會用實際檢查時間來替換它
        if current_time_str[:2] == "12":  # 檢查是否為特定時間
            response = []
            columns = []

            for store in stores:  # Iterate over predefined list of stores
                place, store_name, vegetarian, phone, item, week_schedule, menu_url = (
                    store
                )

                # Check if the user's preference matches the store's vegetarian status
                if (data[1] == "True" and vegetarian) or (
                    data[1] == "False" and not vegetarian
                ):
                    # Create a column for each matching store
                    actions = [URIAction(label="撥打電話", uri=f"tel:{phone.strip()}")]

                    # Conditionally add the 查看菜單 button
                    if menu_url != "none":
                        actions.append(
                            URIAction(label="查看菜單", uri=f"{menu_url.strip()}")
                        )

                    column = CarouselColumn(
                        title=f"{store_name} - {'素食' if vegetarian else '非素食'}",  # 簡單示例標題
                        text=f"營業中 | {item}",
                        actions=actions,
                    )
                    columns.append(column)

            if columns:
                # Create a carousel template message with all the columns
                carousel_template = CarouselTemplate(columns=columns)
                template_message = TemplateSendMessage(
                    alt_text="Store Information",  # Alternative text for devices that do not support templates
                    template=carousel_template,
                )
                # Use the LINE bot API to reply with the template message
                line_bot_api.reply_message(event.reply_token, template_message)
            else:
                # Reply with a simple text message if no stores match
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="沒有找到符合的店家。")
                )

    elif data[0:4] == "rich":
        pass
    else:
        language_responses = {
            "zh-TW": "您已選擇中文介面。",
            "en": "Hello! You have chosen the English interface.",
            "ma": "Hai! Anda telah memilih antara muka Bahasa Melayu.",
            "ja": "こんにちは！日本語インターフェースを選択しました。",
            "ko": "안녕하세요! 한국어 인터페이스를 선택하셨습니다.",
            "vi": "Xin chào! Bạn đã chọn giao diện Tiếng Việt.",
        }
        response_text = language_responses.get(data, "Language not supported.")
        response = TextSendMessage(text=response_text)
        line_bot_api.reply_message(event.reply_token, response)
