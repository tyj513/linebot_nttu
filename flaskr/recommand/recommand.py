import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import re

corpus = [
    "臺東大學擁有優秀的師資和豐富的教學資源。",
    "臺灣台東縣的自然風景優美，吸引了眾多遊客前來觀光。",
]
jieba.load_userdict("test.txt")


def clean_text(text):
    text = re.sub(r"[^\w\s]", "", text)
    return text


def chinese_tokenizer(text):
    text = clean_text(text)
    words = jieba.cut(text)
    return list(words)


tfidf_vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer)
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
feature_names = tfidf_vectorizer.get_feature_names_out()
for i, doc in enumerate(corpus):
    print(f"文本 {i+1} 的關鍵字和對應的 TF-IDF 值：")
    doc_tfidf = [
        (feature_names[index], tfidf_matrix[i, index])
        for index in tfidf_matrix[i, :].nonzero()[1]
    ]
    for word, score in sorted(doc_tfidf, key=lambda x: x[1], reverse=True):
        print(f"{word}: {score:.3f}")
