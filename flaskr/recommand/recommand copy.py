import jieba

# 宣告字串
sentence = "臺東大學是位於臺灣台東縣臺東市的綜合型國立大學，前身爲1948年創立的臺灣省立東師範學校。"
jieba.load_userdict("test.txt")
# 斷詞

## 全模式
s1_list = jieba.cut(sentence, cut_all=True)
print("模式- 全  ： ", " | ".join(s1_list))

## 精確模式
s2_list = jieba.cut(sentence, cut_all=False)
print("模式- 精確： ", " | ".join(s2_list))

## 預設模式
s3_list = jieba.cut(sentence)
print("模式- 預設： ", " | ".join(s3_list))

## 搜尋引擎模式
s4_list = jieba.cut_for_search(sentence)
print("模式- 搜尋： ", " | ".join(s4_list))
