from starlette.responses import StreamingResponse, JSONResponse
from fastapi import status, HTTPException, FastAPI, Body
import uvicorn
from settings import get_response
from utils import load_account, load_chats

app = FastAPI()

@app.post("/response/{user_id}")
async def response(user_id: str, data: dict = Body(...)):
    try:
        # get_response(user_id, data)
        # return StreamingResponse("oke")
        return StreamingResponse(get_response(user_id, data), media_type="text/plain; charset=utf-8")
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.get("/login/{user_id}")
def login(user_id: str):
    """Handles user login by user ID."""
    user_data = load_account(user_id)
    
    if "error" not in user_data:
        user_data["chats"] = load_chats(user_id)  # Attach chat history
    
    return JSONResponse(content=user_data, status_code=status.HTTP_200_OK)

@app.post("/login")
def login_p(data: dict = Body(...)):
    """Handles user login with username & password."""
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username or password.")

    user_data = load_account(username)

    if "error" in user_data:
        return JSONResponse(content=user_data, status_code=status.HTTP_404_NOT_FOUND)

    if username == user_data.get("username") and password == user_data.get("password"):
        user_data["chats"] = load_chats(username)  # Attach chat history
    else:
        return JSONResponse(content={"error": "fail"}, status_code=status.HTTP_401_UNAUTHORIZED)

    return JSONResponse(content=user_data, status_code=status.HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1237)
