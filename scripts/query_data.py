from sentence_transformers import SentenceTransformer
import torch
from splade.models.transformer_rep import Splade
from transformers import AutoTokenizer
import pinecone

class vector_search:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
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
        with torch.no_grad():
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

print("hell")