from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body, HTTPException, status
from starlette.responses import StreamingResponse, JSONResponse
import uvicorn
from modules.configs import CHATS_PATH, RECORDS_PATH
import speech_recognition as sr
import json
import os
import subprocess
from datetime import datetime
from settings import get_response
from utils import load_account, load_chats

os.makedirs(RECORDS_PATH, exist_ok=True)
os.makedirs(CHATS_PATH, exist_ok=True)

app = FastAPI()

class AudioHandler:
    def __init__(self, sub_path):
        self.current_chunks = []
        self.RATE = 44100
        self.CHANNELS = 1
        self.SAMPWIDTH = 2
        self.sub_path = sub_path
        os.makedirs(f'{RECORDS_PATH}/{self.sub_path}', exist_ok=True)

    def save_recording(self):
        if not self.current_chunks:
            return None
        
        webm_data = b''.join(self.current_chunks)
        temp_webm = "temp.webm"
        with open(temp_webm, "wb") as f:
            f.write(webm_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RECORDS_PATH}/{self.sub_path}/recording_{timestamp}.wav"
        
        try:
            command = [
                "ffmpeg", "-i", temp_webm,
                "-ac", str(self.CHANNELS),
                "-ar", str(self.RATE),
                "-sample_fmt", "s16",
                filename
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Recording saved successfully: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Conversion error: {e.stderr.decode()}")
            return None
        finally:
            if os.path.exists(temp_webm):
                os.remove(temp_webm)
        
        self.current_chunks = []
        return filename

@app.websocket("/ws/audio/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id):
    await websocket.accept()
    recognizer = sr.Recognizer()
    audio_handler = AudioHandler(sub_path=user_id)

    try:
        while True:
            message = await websocket.receive()
            
            if "text" in message:  # Text message
                try:
                    data = json.loads(message["text"])
                    if data.get("command") == "start_recognition":
                        filename = audio_handler.save_recording()
                        
                        if filename:
                            try:
                                with sr.AudioFile(filename) as source:
                                    audio = recognizer.record(source)
                                    try:
                                        text = recognizer.recognize_google(audio, language="vi-VN")
                                        response = {
                                            "status": "success",
                                            "text": text,
                                            "filename": filename
                                        }
                                    except sr.UnknownValueError:
                                        response = {
                                            "status": "error",
                                            "message": "Speech not detected or unclear",
                                            "filename": filename
                                        }
                                    except sr.RequestError as e:
                                        response = {
                                            "status": "error",
                                            "message": f"API Error: {str(e)}",
                                            "filename": filename
                                        }
                                    
                                    await websocket.send_json(response)
                            except Exception as e:
                                await websocket.send_json({
                                    "status": "error",
                                    "message": f"File processing error: {str(e)}",
                                    "filename": filename
                                })
                except json.JSONDecodeError:
                    print("Received non-JSON message:", message)

            elif "bytes" in message:  # Binary audio data
                print(f"Received audio data: {len(message['bytes'])} bytes")
                audio_handler.current_chunks.append(message['bytes'])

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")

@app.post("/response/{user_id}")
async def response(user_id: str, data: dict = Body(...)):
    try:
        return StreamingResponse(get_response(user_id, data), media_type="text/plain; charset=utf-8")
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/login")
def login_p(data: dict = Body(...)):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username or password.")

    user_data = load_account(username)

    if "error" in user_data:
        return JSONResponse(content=user_data, status_code=status.HTTP_404_NOT_FOUND)

    if username == user_data.get("username") and password == user_data.get("password"):
        user_data["chats"] = load_chats(username)
    else:
        return JSONResponse(content={"error": "fail"}, status_code=status.HTTP_401_UNAUTHORIZED)

    return JSONResponse(content=user_data, status_code=status.HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1237)