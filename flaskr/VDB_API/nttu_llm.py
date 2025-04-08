from typing import Any, Dict, List, Union
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from flaskr.VDB_API.utils import file_processor
from flaskr.VDB_API.utils.config import CHAT_MODELS, DEVICE, PROMPT_TEMPLATE
from flaskr.VDB_API.vectordb_manager import VectordbManager
from flaskr.VDB_API.utils.transfer_chinese import (
    traditional_to_simplified,
    simplified_to_traditional,
)


class NTTU_tools:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            CHAT_MODELS["offline"],
            trust_remote_code=True,
            use_auth_token="",
        )

        self.llm = AutoModelForCausalLM.from_pretrained(  # 條參數
            CHAT_MODELS["offline"],
            device_map="auto",
            trust_remote_code=True,
            use_auth_token="",
        ).eval()

        self.vectordb_manager = VectordbManager()
        self.file_path = []
        self.files = []

    def set_llm(self, llm_type: str):
        print("Your device: ", DEVICE)
        model = AutoModelForCausalLM.from_pretrained(
            CHAT_MODELS[llm_type], trust_remote_code=True, device_map="auto"
        ).eval()
        pipe = pipeline(
            "text-generation",
            model=model.to(DEVICE),
            tokenizer=self.tokenizer,
            max_new_tokens=100,
        )
        print("set chat model to ", CHAT_MODELS[llm_type])
        return HuggingFacePipeline(pipeline=pipe)

    def add_documents_to_vdb(self, file_paths: List[str]):
        """
        Arg:
            file_paths: 文件路徑 list (需含檔名)
        """
        self.file_path = file_paths
        for file_path in file_paths:
            texts, file_name = file_processor.get_split_data(file_path)
            self.files.append(file_name)
            self.vectordb_manager.add(texts)

    def chat(self, query: str):
        docs = []
        tmp_docs = self._search_vdb(query)
        docs = file_processor.add_unique_docs(docs, tmp_docs)
        ans = self._get_llm_reply(query, docs)
        contents, metadatas = [], []
        """
         for doc in docs:
            tmp_content = doc.page_content.split("--")
            print("111111111111111111")
            print(tmp_content)
            tmp_content = "".join(tmp_content[1:])
            print("22222222222")
            print(tmp_content)
            contents.append(tmp_content)
            metadatas.append(doc.metadata)
        """

        print("ans:", ans)
        print("contents:", contents)
        print("metadatas:", metadatas)
        return ans, contents, metadatas

    def _search_vdb(self, query):
        where = self._get_filter(self.files)
        docs = self.vectordb_manager.query(query, n_results=3, where=where)
        return docs

    def _get_filter(self, file_list) -> Union[Dict[str, Any], None]:
        if len(file_list) == 1:
            return {"source": file_list[0]}
        elif len(file_list) > 1:
            return {"$or": [{"source": name} for name in file_list]}
        else:
            raise ValueError("file_list is empty")

    # 找到的資料!!!!!!!!!!!!!!!!!!! 輸出的答案
    def _get_llm_reply(self, query, docs):
        templated_query = PROMPT_TEMPLATE.format(query=query)
        contents = ""
        for doc in docs:
            contents += doc.page_content + "\n"
        print("contents:", contents)
        print("templated_query:", templated_query)

        question = traditional_to_simplified(
            f"[參考資料] {contents} \n" + templated_query
        )
        print(question)

        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        ans, _ = self.llm.chat(self.tokenizer, question, history=None)
        ans = simplified_to_traditional(ans)
        return ans
