import sys
import configparser
from linebot import LineBotApi
import requests
import json


# get channel_access_token 、 line_bot_api and headers information
config = configparser.ConfigParser()
# 注意 config.ini 的寫法，因為 config.ini 是在該檔案所在的資料夾外面一層。
config.read("../config_copy.ini")
# 取得 Line Bot 的 channel-access-token
channel_access_token = config.get("line-bot", "channel_access_token")

# 取得 channel-access-token。如果沒有確實取得，則 print 出相應的警告並結束程式
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)
else:
    line_bot_api = LineBotApi(channel_access_token)
    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": "application/json",
    }


# get the rich menu list, and delete all rich menu
rich_menu_list = line_bot_api.get_rich_menu_list()
for rich_menu in rich_menu_list:
    print("Delete Rich Menu ID :", rich_menu.rich_menu_id)
    line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)

# get the rich menu alias list, and delete all rich menu alias
alias_list = requests.get(
    "https://api.line.me/v2/bot/richmenu/alias/list", headers=headers
).json()["aliases"]
for alias in alias_list:
    print("Delete Rich Menu Alias ID :", alias)
    req = requests.delete(
        "https://api.line.me/v2/bot/richmenu/alias/" + alias["richMenuAliasId"],
        headers=headers,
    )


# 設定第一個 richmenu 的內容，設定的重點如下：
## 1. name 設定為 first(可更改，自己記得就好)，表示別名 Alias Id。
## 2. 除了要進行切換的按鈕外，其他同單個RichMenu設計方式。
## 3. 連結到選單 B 的按鈕，設定為 richmenuswitch，richMenuAliasId 設定為 Alias_A。
body_A = {
    "size": {"width": 2500, "height": 1686},  # 設定尺寸
    "selected": "true",  # 預設是否顯示
    "name": "first",  # 選單名稱
    "chatBarText": "我是範例A",  # 選單在 LINE 顯示的標題
    "areas": [  # 選單內容
        {
            "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},  # 選單位置與大小
            "action": {"type": "message", "text": "A"},  # 點擊後傳送文字
        },
        {
            "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},  # 選單位置與大小
            "action": {"type": "message", "text": "B"},  # 點擊後傳送文字
        },
        {
            "bounds": {
                "x": 1667,
                "y": 0,
                "width": 833,
                "height": 843,
            },  # 選單位置與大小
            "action": {"type": "message", "text": "C"},  # 點擊後傳送文字
        },
        {
            "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},  # 選單位置與大小
            "action": {"type": "message", "text": "D"},  # 點擊後傳送文字
        },
        {
            "bounds": {
                "x": 833,
                "y": 843,
                "width": 834,
                "height": 843,
            },  # 選單位置與大小
            "action": {"type": "message", "text": "E"},  # 點擊後傳送文字
        },
        {
            "bounds": {
                "x": 1667,
                "y": 843,
                "width": 833,
                "height": 843,
            },  # 選單位置與大小
            "action": {
                "type": "richmenuswitch",
                "richMenuAliasId": "second",
                "data": "change-to-second",
            },  # 點擊後傳送文字
        },
    ],
}
req_richmenu_A = requests.post(
    "https://api.line.me/v2/bot/richmenu",
    headers=headers,
    data=json.dumps(body_A).encode("utf-8"),
)
# 可以透過打印 req_richmenu_A 查看 requests.post 的結果，若程式執行成功會回傳 <Response [200]>。
print("req", req_richmenu_A)


# 上方程式碼執行後，會得到 richmenu A 的 id，將 id、圖片在雲端硬碟中的位址、access token 填入下方程式碼，執行後就會將圖片與 richmenu 綁定
rich_menu_A_name = req_richmenu_A.json()["richMenuId"]

print("New Rich Menu ID :", rich_menu_A_name)
rich_menu_A_name2 = rich_menu_A_name[9:]
print("New Rich Menu ID :", rich_menu_A_name2)

# 設定第一個 richmenu 上的照片
with open(
    "/home/p76131694/AutoReply-LineBotAssistant/flaskr/image/richmenu_example.png", "rb"
) as f:
    line_bot_api.set_rich_menu_image(rich_menu_A_name, "image/png", f)


# 將 richmenu id 和別名與 Alias id 綁定。
alias_body_A = {"richMenuAliasId": "first", "richMenuId": rich_menu_A_name}
alias_req_A = requests.post(
    "https://api.line.me/v2/bot/richmenu/alias",
    headers=headers,
    data=json.dumps(alias_body_A).encode("utf-8"),
)
# 可以透過打印 alias_req_A 查看 requests.post 的結果，若程式執行成功會回傳 <Response [200]>。
# print(alias_req_A)

# 將 richmenu 傳送到對應的 Line Bot。
req_A = requests.post(
    "https://api.line.me/v2/bot/user/all/richmenu/" + rich_menu_A_name, headers=headers
)
# 可以透過打印 req_A 查看 requests.post 的結果，若程式執行成功會回傳 <Response [200]>。
# print(req_A)

# 設定第二個 richmenu 的內容，設定的重點如下：
## 1. name 設定為 second(可更改，自己記得就好)，表示別名 Alias Id。
## 2. 除了要進行切換的按鈕外，其他同單個 richmenu 設計方式。
## 3. 連結到選單 B 的按鈕，設定為 richmenuswitch，richMenuAliasId 設定為 Alias_A。
body_B = {
    "size": {"width": 2500, "height": 1686},  # 設定尺寸
    "selected": "true",  # 預設是否顯示
    "name": "second",  # 選單名稱
    "chatBarText": "我是範例B",  # 選單在 LINE 顯示的標題
    "areas": [  # 選單內容
        {
            "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},  # 選單位置與大小
            "action": {"type": "message", "text": "F"},  # 點擊後傳送文字
        },
        {
            "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},  # 選單位置與大小
            "action": {"type": "message", "text": "G"},  # 點擊後傳送文字
        },
        {
            "bounds": {
                "x": 1667,
                "y": 0,
                "width": 833,
                "height": 843,
            },  # 選單位置與大小
            "action": {"type": "message", "text": "H"},  # 點擊後傳送文字
        },
        {
            "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},  # 選單位置與大小
            "action": {"type": "message", "text": "I"},  # 點擊後傳送文字
        },
        {
            "bounds": {
                "x": 833,
                "y": 843,
                "width": 834,
                "height": 843,
            },  # 選單位置與大小
            "action": {"type": "message", "text": "J"},  # 點擊後傳送文字
        },
        {
            "bounds": {
                "x": 1667,
                "y": 843,
                "width": 833,
                "height": 843,
            },  # 選單位置與大小
            "action": {
                "type": "richmenuswitch",
                "richMenuAliasId": "first",
                "data": "change-to-first",
            },  # 點擊後傳送文字
        },
    ],
}

req_richmenu_B = requests.post(
    "https://api.line.me/v2/bot/richmenu",
    headers=headers,
    data=json.dumps(body_B).encode("utf-8"),
)
# 可以透過打印 req_richmenu_B 查看 requests.post 的結果，若程式執行成功會回傳 <Response [200]>。
# print(req_richmenu_B)


# 上方程式碼執行後，會得到 richmenu B 的 id，將 id、圖片在雲端硬碟中的位址、access token 填入下方程式碼，執行後就會將圖片與圖文選單綁定
rich_menu_B_name = req_richmenu_B.json()["richMenuId"]
print("New Rich Menu ID :", rich_menu_B_name)

# 設定第二個 richmenu 上的照片
with open(
    "/home/p76131694/AutoReply-LineBotAssistant/flaskr/image/choose2.png", "rb"
) as f:
    line_bot_api.set_rich_menu_image(rich_menu_B_name, "image/png", f)


# 將 richmenu id 和別名與 Alias id 綁定。
alias_body_B = {"richMenuAliasId": "second", "richMenuId": rich_menu_B_name}
alias_req_B = requests.post(
    "https://api.line.me/v2/bot/richmenu/alias",
    headers=headers,
    data=json.dumps(alias_body_B).encode("utf-8"),
)
# 可以透過打印 alias_req_B 查看 requests.post 的結果，若程式執行成功會回傳 <Response [200]>。
# print(alias_req_B)
