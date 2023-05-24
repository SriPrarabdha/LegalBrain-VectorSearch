import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer
import pinecone

data = pd.read_csv('law_gpt\data\constitution\Constitution Of India.csv')
laws = list(data['Articles'])
for i in range(len(laws)):
    laws[i] = 'Article ' + laws[i]

data = []

for i, context in enumerate(laws):
        data.append({
            'id': f"{i}",
            'context': context
        })

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# check device being run on
if device != 'cuda':
    print("WARNING: No GPU")

dense_model = SentenceTransformer(
    'msmarco-bert-base-dot-v5',
    device=device
)

from splade.models.transformer_rep import Splade

sparse_model_id = 'naver/splade-cocondenser-ensembledistil'

sparse_model = Splade(sparse_model_id, agg='max')
sparse_model.to(device)

tokenizer = AutoTokenizer.from_pretrained(sparse_model_id)

def builder(records: list):
    ids = [x['id'] for x in records]
    contexts = [x['context'] for x in records]
    # create dense vecs
    dense_vecs = dense_model.encode(contexts).tolist()
    # create sparse vecs
    input_ids = tokenizer(
        contexts, return_tensors='pt',
        padding=True, truncation=True
    )
    with torch.no_grad():
        sparse_vecs = sparse_model(
            d_kwargs=input_ids.to(device)
        )['d_rep'].squeeze()
    # convert to upsert format
    upserts = []
    for _id, dense_vec, sparse_vec, context in zip(ids, dense_vecs, sparse_vecs, contexts):
        # extract columns where there are non-zero weights
        indices = sparse_vec.nonzero().squeeze().cpu().tolist()  # positions
        values = sparse_vec[indices].cpu().tolist()  # weights/scores
        # build sparse values dictionary
        sparse_values = {
            "indices": indices,
            "values": values
        }
        # build metadata struct
        metadata = {'context': context}
        # append all to upserts list as pinecone.Vector (or GRPCVector)
        upserts.append({
            'id': _id,
            'values': dense_vec,
            'sparse_values': sparse_values,
            'metadata': metadata
        })
    return upserts

pinecone.init(
    api_key="f112db94-1b02-44ec-b1d7-a4cf165fad28",  # app.pinecone.io
    environment="us-east1-gcp"  # next to api key in console
)

index_name = 'law-gpt'

pinecone.create_index(
    index_name,
    dimension=768,
    metric="dotproduct",
    pod_type="s1"
)

index = pinecone.GRPCIndex(index_name)
index.describe_index_stats()

batch_size = 64

for i in range(0, len(data), batch_size):
    # extract batch of data
    i_end = min(i+batch_size, len(data))
    batch = data[i:i_end]
    # pass data to builder and upsert
    index.upsert(builder(data[i:i+batch_size]))