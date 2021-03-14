from typing import Optional

from fastapi import FastAPI

app = FastAPI()


# comment!

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/createRepository")
async def read_item(user: str, repo_name: str):
    return {"status": f"Repo was created for user {user} with name {repo_name}"}
