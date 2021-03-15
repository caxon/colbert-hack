from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
import os

from colbert.retrieve import init_retrieve, retrieve_query

######################
## HELPER FUNCTIONS ##
######################

def load_document_collection(path):
    docs = []
    with open(os.getcwd() + "/data/wwii.tsv") as tsv_file:
        reader = csv.reader(tsv_file, delimiter="\t")
        for line in reader:
            docs.append(line[1])
    return docs

###################
##### ROUTES ######
###################
app = FastAPI()

origins = [
    'http://localhost:3001',
    'http://localhost:3000',
    'https://colbert-hack.netlify.app'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/createRepository")
async def create_repo(user: str, repo_name: str):
    return {"status": f"Repo was created for user {user} with name {repo_name}"}

@app.post("/query")
async def single_query(query: str):
    if query == "":
        return {"status":"error", "message": "Must provide a query"}

    print("STARTING QUERY RETRIEVAL -- q:", query)
    ranking = retrieve_query(query)
    print("QUERY HAS BEEN RETRIEVED")

    readible_mapping = list ( map(lambda x: (docs[x[0]], x[1]), ranking) )

    return {"status": "success", "original_query": query, "matches": readible_mapping[:30]}


####################
## INITIALIZATION ##
####################
init_retrieve()

docs = load_document_collection('./data/collections.10k.tsv')

print("-- server initialized")
