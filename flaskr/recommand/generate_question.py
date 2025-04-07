"""
import jieba
from collections import Counter
import jieba.analyse

# 加載自定義詞典
file_path = "custom_dict.txt"
jieba.load_userdict(file_path)

# 定義文本
text = "抱歉，參考資料中沒有台東大學學生會費的相關信息，因此無法確定學生會費是否每學年一次性繳納以及是否強制。建議諮詢相關學校部門或學生會以獲得更準確的資訊。"

# 使用 jieba 的 extract_tags 函数提取关键字
keywords = jieba.analyse.extract_tags(text, topK=5)
 
"""

# 1. Install necessary modules:
# You should run this in your terminal or appropriate install environment:
# pip install sentence-transformers transformers spacy sklearn

# 2. Import necessary modules
from sentence_transformers import SentenceTransformer
from transformers import (
    T5ForConditionalGeneration,
    AutoTokenizer,
    BertTokenizer,
    BertModel,
)
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import spacy
from warnings import filterwarnings as filt

filt("ignore")

# 3. Initialize the pre-trained models
bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertModel.from_pretrained("bert-base-uncased")
model = SentenceTransformer("distilbert-base-nli-mean-tokens")
nlp = spacy.load("en_core_web_sm")
"""
bert_tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
bert_model = BertModel.from_pretrained("bert-base-chinese")

# 加载T5中文问答模型
question_model = AutoModelForSeq2SeqLM.from_pretrained(
    "uer/t5-base-chinese-cluecorpussmall"
)
question_tokenizer = AutoTokenizer.from_pretrained(
    "uer/t5-base-chinese-cluecorpussmall"
)
"""
translator_model_name = "Helsinki-NLP/opus-mt-zh-en"
translator_tokenizer = AutoTokenizer.from_pretrained(translator_model_name)
translator_model = AutoModelForSeq2SeqLM.from_pretrained(translator_model_name)

translator_en_to_zh_model_name = "Helsinki-NLP/opus-mt-en-zh"
translator_en_to_zh_tokenizer = AutoTokenizer.from_pretrained(
    translator_en_to_zh_model_name
)
translator_en_to_zh_model = AutoModelForSeq2SeqLM.from_pretrained(
    translator_en_to_zh_model_name
)


def translate(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text


# 4. Create a function for generating a question.
def get_question(sentence, answer):
    mdl = T5ForConditionalGeneration.from_pretrained("ramsrigouthamg/t5_squad_v1")
    tknizer = AutoTokenizer.from_pretrained("ramsrigouthamg/t5_squad_v1")

    text = f"context: {sentence} answer: {answer}"
    encoding = tknizer.encode_plus(
        text, max_length=256, truncation=True, return_tensors="pt"
    )
    input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

    outs = mdl.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        early_stopping=True,
        num_beams=5,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        max_length=300,
    )

    dec = [tknizer.decode(ids, skip_special_tokens=True) for ids in outs]
    question = dec[0].replace("question:", "").strip()
    return question


# 5. Create another function to generate meaningful keywords (answers)
def get_embedding(doc):
    # Tokenize the document
    inputs = bert_tokenizer(doc, return_tensors="pt", max_length=512, truncation=True)
    # Get BERT outputs
    outputs = bert_model(**inputs)

    # Use mean pooling to get a single vector for the entire document
    # outputs.last_hidden_state has shape [batch_size, sequence_length, hidden_size]
    # We take the mean of the second dimension (sequence_length) to get [batch_size, hidden_size]
    embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()

    return embeddings


def get_sent(context):
    doc = nlp(context)
    return list(doc.sents)


def get_vector(doc):
    stop_words = "english"
    n_gram_range = (1, 1)
    vectorizer = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words)
    vectorizer.fit([doc])
    return vectorizer.get_feature_names_out()


def get_key_words(context, module_type="t"):
    keywords = []
    top_n = 5
    for txt in get_sent(context):
        keywd = get_vector(str(txt))
        print(f"vectors: {keywd}")
        if module_type == "t":
            doc_embedding = get_embedding(str(txt))
            keywd_embeddings = [get_embedding(word) for word in keywd]
        else:
            doc_embedding = model.encode([str(txt)])
            keywd_embeddings = model.encode(keywd)

        # Convert list of embeddings into an array
        keywd_embeddings = np.vstack(keywd_embeddings)

        # Calculate cosine similarity between document embedding and each keyword embedding
        distances = cosine_similarity(doc_embedding, keywd_embeddings)
        print(distances)
        keywords += [
            (keywd[index], str(txt)) for index in distances.argsort()[0][-top_n:]
        ]

    return keywords


# Example usage
txt = "特別的會員禮物（如抱枕）將在學生會整理名單後發放。具體時間和地點會透過Dcard、Instagram和LINE等渠道公告。"
translated_text = translate(txt, translator_model, translator_tokenizer)
keywords = get_key_words(translated_text)
print(keywords)


# Generate a question using the extracted keyword
for keyword, sentence in keywords:
    print(f"Generated Question: {get_question(sentence, keyword)}")
