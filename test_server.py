from typing import Generator
from starlette.responses import StreamingResponse, JSONResponse
from fastapi import status, HTTPException, FastAPI
import uvicorn
from settings import chain, history
import time

def chat_llm(input):
    for chunk in chain.invoke(input):
        yield str(chunk)
        print(chunk)
        history[-1]['assistant'] += chunk

def chat_llm2(input):
    res = ""
    for chunk in chain.invoke(input):
        res += str(chunk)
    return res

# Now response the API
app = FastAPI()

@app.post("/response/")
async def get_response(data: dict):
    try:
        history.append({
            "user":data['query'],
            "assistant":"",
        })
        return StreamingResponse(chat_llm(data['query']), media_type="text/plain; charset=utf-8")
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)
    
@app.post("/answer/")
async def get_response(data: dict):
    try:
        return JSONResponse({"answer":chat_llm2(data['query'])})
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)
    
if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=1237)
