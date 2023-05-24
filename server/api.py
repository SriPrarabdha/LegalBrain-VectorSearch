from typing import Any, Dict, List

import langchain
from langchain import VectorDBQAWithSourcesChain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from steamship import File
from steamship.invocable import PackageService, post

from steamship_langchain.cache import SteamshipCache
from steamship_langchain.llms import OpenAI
from steamship_langchain.vectorstores import SteamshipVectorStore

from sentence_transformers import SentenceTransformer
# import torch
from splade.models.transformer_rep import Splade
from transformers import AutoTokenizer
import pinecone

class vector_search:
    def __init__(self):
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = 'cpu'
        self.dense_model = SentenceTransformer(
            'msmarco-bert-base-dot-v5',
            device=self.device
        )
        sparse_model_id = 'naver/splade-cocondenser-ensembledistil'

        self.sparse_model = Splade(sparse_model_id, agg='max')
        self.sparse_model.to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(sparse_model_id)

    def get_pinecone(self , index):
        pinecone.init(
            api_key="f112db94-1b02-44ec-b1d7-a4cf165fad28",  
            environment="us-east1-gcp"  
        )

        self.index = pinecone.Index(index)
        print(self.index.describe_index_stats())
        return self.index
    
    def encode(self , text: str):
    # create dense vec
        dense_vec = self.dense_model.encode(text).tolist()
    # create sparse vec
        input_ids = self.tokenizer(text, return_tensors='pt')
        # with torch.no_grad():
        sparse_vec = self.sparse_model(
            d_kwargs=input_ids.to(self.device)
        )['d_rep'].squeeze()
    # convert to dictionary format
        indices = sparse_vec.nonzero().squeeze().cpu().tolist()
        values = sparse_vec[indices].cpu().tolist()
        sparse_dict = {"indices": indices, "values": values}
    # return vecs
        return dense_vec, sparse_dict

    def query(self , q:str):
        # query = "Who is the Chief Justice of High Court when the seat is vacant"
        dense, sparse = self.encode(q)
# query
        xc = self.index.query(
            vector=dense,
            sparse_vector=sparse,
            top_k=2,  # how many results to return
            include_metadata=True
        )
        return xc


class QuestionAnsweringPackage(PackageService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # set up LLM cache
        langchain.llm_cache = SteamshipCache(self.client)
        # set up LLM
            #self.llm = OpenAI(client=self.client, temperature=0, cache=True, max_words=250)
        # create a persistent embedding store
            # self.index = SteamshipVectorStore(
            #     client=self.client, index_name="qa-demo", embedding="text-embedding-ada-002"
            # )
        self.v = vector_search()
        self.index = self.v.get_pinecone("law-gpt")

    @post("sd_vector_search")
    def sd_vector_search(self , text:str):
        return self.v.query(text)
    
    # @post("index_file")
    # def index_file(self, file_handle: str) -> bool:
    #     text_splitter = CharacterTextSplitter(chunk_size=250, chunk_overlap=0)
    #     file = File.get(self.client, handle=file_handle)
    #     texts = [text for block in file.blocks for text in text_splitter.split_text(block.text)]
    #     metadatas = [{"source": f"{file.handle}-offset-{i * 250}"} for i, text in enumerate(texts)]

    #     self.index.add_texts(texts=texts, metadatas=metadatas)
    #     return True

    # @post("search_embeddings")
    # def search_embeddings(self, query: str, k: int) -> List[Document]:
    #     """Return the `k` closest items in the embedding index."""
    #     return self.index.similarity_search(query, k=k)

    # @post("/qa_with_sources")
    # def qa_with_sources(self, query: str) -> Dict[str, Any]:
    #     chain = VectorDBQAWithSourcesChain.from_chain_type(
    #         OpenAI(client=self.client, temperature=0),
    #         chain_type="stuff",
    #         vectorstore=self.index,
    #         return_source_documents=True,
    #     )

    #     return chain({"question": query})