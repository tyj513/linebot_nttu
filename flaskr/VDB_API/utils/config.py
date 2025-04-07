# vector database settings
HUGGINGFACE_MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "basic"

# file_processor.py setting
LANG_SEARCH_SIZE = 2000
EN_CHUNK_SIZE = 1000
EN_CHUNK_OVERLAP = 400
ZH_CHUNK_SIZE = 400
ZH_CHUNK_OVERLAP = 200

# for hacker_rank_tools.py
CHAT_MODELS = {
    "gpt3": "gpt-3.5-turbo",
    "gpt4": "gpt-4-0613",
    # "offline": "bigscience/bloomz-7b1",
    "offline": "Qwen/Qwen-7B-Chat",  #     "offline": "taide/TAIDE-LX-7B-Chat",
}
PROMPT_TEMPLATE = """
我希望你是一位對兩岸關係相關用語非常小心的人，回答問題請避免用"臺灣省"或"中華民國"等字眼進行稱呼，直接用台灣就好，政治相關人物的名字也一概不要做出回應，就說不知道或不清楚。如果參考資料沒有說到也直接明說不知道。
請幫我回答下列問題 :
{query}
"""

# general
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
