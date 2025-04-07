from linebot.models import *


class ButtonTemplateInfo:
    def __init__(self, url, title, text, keywords, questions):
        self.url = url
        self.title = title
        self.text = text
        self.keywords = keywords
        self.questions = questions

    def display_info(self):
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print(f"URL: {self.url}")
        print(f"Title: {self.title}")
        print(f"Text: {self.text}")
        print("Keyword and Questions:")
        for keyword, question in zip(self.keywords, self.questions):
            print(f"Keyword: {keyword}")
            print(f"Question: {question}")


class FeeButtonInfo(ButtonTemplateInfo):
    def __init__(self):
        url = "https://raw.githubusercontent.com/tyj513/audio/main/b.png"
        title = "台東大學費用相關問題"
        text = "請點選(或直接用對話框提問)"
        keywords = [
            "學生會費要交嗎",
            "學生會費是分期還是一次繳清",
            "學生會晚會邀請哪些藝人",
            "新生何時領學生會員禮物",
        ]
        questions = [
            "台東大學的學生會費是每學年一次性支付的嗎？ 是否強制性繳納？",
            "在台東大學，學生會費是分期繳納還是一次繳清？",
            "過去台東大學學生會的聖誕晚會都邀請了哪些藝人？",
            "剛入學並繳納學生會費的新生，何時可以領取會員禮物？",
        ]
        super().__init__(url, title, text, keywords, questions)


class TransportationButtonInfo(ButtonTemplateInfo):
    def __init__(self):
        url = "https://raw.githubusercontent.com/tyj513/audio/main/d.png"
        title = "台東大學交通相關問題"
        text = "請點選(或直接用對話框提問)"
        keywords = [
            "怎麼去台東大學",
            "知本火車站怎樣到達台東大學",
            "學校裡有什麼交通工具",
            "假期車票容易訂嗎",
        ]
        questions = [
            "怎麼去台東大學?",
            "從知本火車站怎樣到達台東大學？",
            "在台東大學的交通工具有哪些？",
            "假期時從台東大學回家的車票容易訂到嗎？",
        ]
        super().__init__(url, title, text, keywords, questions)


class AffairButtonInfo(ButtonTemplateInfo):
    def __init__(self):
        url = "https://raw.githubusercontent.com/tyj513/audio/main/a.png"
        title = "台東大學校務相關問題"
        text = "請點選(或直接用對話框提問)"
        keywords = ["社團參與上限", "校內提款機位置", "一個月生活費推估", "日用品購買"]
        questions = [
            "在台東大學，一個學生可以參加幾個社團？",
            "台東大學校園內有哪些地方設有提款機？",
            "在台東大學，一個月的生活費大概需要多少？",
            "台東大學的日用品在哪裡可以購買？",
        ]
        super().__init__(url, title, text, keywords, questions)


class ActivityButtonInfo(ButtonTemplateInfo):
    def __init__(self):
        url = "https://raw.githubusercontent.com/tyj513/audio/main/f.png"
        title = "台東大學生活相關問題"
        text = "請點選(或直接用對話框提問)"
        keywords = ["校內活動", "校外活動", "社團活動", "學生會活動"]
        questions = [
            "台東大學校內有哪些活動？",
            "台東大學校外有哪些活動？",
            "台東大學有哪些社團？",
            "台東大學學生會有哪些活動？",
        ]
        super().__init__(url, title, text, keywords, questions)


class DomitoryButtonInfo(ButtonTemplateInfo):
    def __init__(self):
        url = "https://raw.githubusercontent.com/tyj513/audio/main/c.png"
        title = "台東大學宿舍相關問題"
        text = "請點選(或直接用對話框提問)"
        keywords = [
            "單人房宿舍價格",
            "二人房宿舍價格",
            "四人房宿舍價格",
            "六人房宿舍價格",
        ]
        questions = [
            "台東大學單人房宿舍價格？",
            "台東大學二人房宿舍價格？",
            "台東大學四人房宿舍價格？",
            "台東大學六人房宿舍價格？",
        ]
        super().__init__(url, title, text, keywords, questions)


class OtherButtonInfo(ButtonTemplateInfo):
    def __init__(self):
        url = "https://raw.githubusercontent.com/tyj513/audio/main/principal2.png"
        title = "台東大學其他常見問題"
        text = "請點選(或直接用對話框提問)"
        keywords = ["台東大學校長", "學校簡介", "學校位置", "學校歷史"]
        questions = [
            "台東大學的校長是誰？",
            "台東大學的簡介？",
            "台東大學的位置？",
            "台東大學的歷史？",
        ]

        super().__init__(url, title, text, keywords, questions)
