from starlette.responses import StreamingResponse
from fastapi import status, HTTPException, FastAPI, Body
import uvicorn
from settings import get_response
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

app = FastAPI()

@app.post("/response/{user_id}")
async def response(user_id: str, data: dict = Body(...)):
    """
    Handle requests with an User ID in the URL and additional data in the body.
    
    Args:
        user_id (str): The User ID passed in the URL.
        data (dict): The additional data sent in the request body.
    
    Returns:
        StreamingResponse: The response stream based on the processed input.
    """
    try:
        # Pass both the ID and the body data to your `get_response` function
        return StreamingResponse(get_response(user_id, data), media_type="text/plain; charset=utf-8")
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1237)
