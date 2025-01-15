from typing import Generator
from starlette.responses import StreamingResponse, JSONResponse
from fastapi import status, HTTPException, FastAPI
import uvicorn
from settings import chat
import time

# Now response the API
app = FastAPI()

@app.post("/response/")
async def get_response(data: dict):
    try:
        return StreamingResponse(chat(data), media_type="text/plain; charset=utf-8")
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=1237)
