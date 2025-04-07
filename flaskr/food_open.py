import datetime


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


# Store information: (place, store_name, vegetarian, phone, item, week_schedule)
stores = [
    (
        "第一學生宿舍餐飲中心",
        "台東佳學便利商店",
        False,
        "0921-599-075",
        "生活用品、雜貨、冷飲、泡麵、零嘴食品",
        ["0-4 07:30-24:00", "5-6 09:30-24:00"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "天使麻辣滷味",
        False,
        "905-817-827",
        "鹵味（乾/湯澜），90多種品項，自由配料",
        ["0-4 11:30-13:00", "0-4 17:00-21:30", "6 17:00-21:30"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "厚道商行",
        False,
        "0908-911-546",
        "便當, 奶酪, 水果, 飲料",
        ["0-4 11:00-13:00", "5 11:00-13:00"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "ALOHA POKE",
        True,
        "0935-355-562",
        "夏威夷蓋飯, 素蔬（紫米飯, 沙拉, 主食, 醬料多元選擇-任意搭配）",
        ["0-4 11:00-14:00", "0-4 17:00-20:00", "4 11:00-13:00"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "小鐵匠廚房",
        False,
        "0907-292-117",
        "蔬食/經濟/雞排/豬排/雞腿等飯類",
        ["0-4 11:00-13:00"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "東大膳綁",
        True,
        "518-003",
        "素蔬、早餐類",
        ["0-4 06:30-14:00", "0-4 17:00-20:00", "6 16:30-20:30"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "炒鬧食堂",
        True,
        "0953-391-961",
        "炒飯、鍋燒麵",
        ["0-4 11:00-14:00", "0-4 16:30-20:30"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "祥瑞食堂",
        False,
        "0976-836-337",
        "麵類、湯品、肉粽、飲料",
        ["0-3 10:00-14:00", "1-2 16:00-20:30", "4 16:00-20:30"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "鼎泰珍牛排館",
        False,
        "0933-626-695",
        "排餐、便當、麵類、菜飯",
        ["0-6 10:00-14:00", "0-6 17:00-20:00"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "巴布阿甘飲食店",
        False,
        "517-518",
        "牛肉麵、乾拌麵、鐵板麵",
        ["0-4 08:00-19:00", "5 11:00-14:30"],
    ),
    (
        "第一學生宿舍餐飲中心",
        "快美廉印刷店",
        False,
        "518-110",
        "影印店",
        ["0-4 11:00-13:30", "0-4 16:30-19:30"],
    ),
    (
        "第二學生宿舍餐飲中心",
        "東大健康茶飲",
        True,
        "517-968",
        "各式飲品（杯裝, 桶裝），水餃，厚片/熱壓吐司，麻油赤肉麵線等麵類",
        ["0-4 10:30-21:00", "5 10:30-14:00"],
    ),
    (
        "第二學生宿舍餐飲中心",
        "7-ELEVEN",
        True,
        "518-145",
        "便利商店",
        ["0-6 06:00-24:00"],
    ),
    (
        "第二學生宿舍餐飲中心",
        "百祥國際嚴選餐飲",
        True,
        "518-006",
        "素蔬, 開會便當-平價自助餐, 多元化選擇•自由搭配（現場場地大螢幕可供開會聚餐）",
        ["0-4 11:00-13:30", "0-4 16:30-20:30", "5 11:00-13:30"],
    ),
    (
        "第二學生宿舍餐飲中心",
        "藜饗食光",
        True,
        "0960-771-020, 0937-602-855",
        "海苔飯手卷, 炊飯, 浦肉飯、肉羹飯（湯），飲品、熱壓吐司、車輪餅",
        ["0-3 09:30-18:30", "4 09:30-13:30"],
    ),
    (
        "第二學生宿舍餐飲中心",
        "妙軒早餐店",
        False,
        "0912-759-332",
        "早餐類",
        ["0-4 07:00-14:00", "5-6 09:00-14:00"],
    ),
    (
        "第二學生宿舍餐飲中心",
        "四海遊龍",
        False,
        "517-918, 0976-770-921",
        "鍋貼連鎖店",
        ["0-4 11:00-20:00", "6 11:00-20:00"],
    ),
]


def ask_vegetarian():
    response = input("您是否需要吃素？(是/否): ")
    return response.strip() == "是"


vegetarian_needed = ask_vegetarian()
print(vegetarian_needed)

# Check each store if it's open now
for store in stores:
    place, store_name, vegetarian, phone, item, week_schedule = store
    if vegetarian == vegetarian_needed and is_open_now(week_schedule):
        print(f"{store_name} 現在是營業時間。")
