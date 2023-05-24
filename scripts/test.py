from query_data import vector_search

v = vector_search()
index = v.get_pinecone("law-gpt")

d , s = v.encode("")