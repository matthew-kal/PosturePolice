from fastapi import FastAPI, WebSocket
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            header, encoded = data.split(",", 1)

            img_data = base64.b64decode(encoded)
            print(f"Decoded image data size: {len(img_data)} bytes")

            image = Image.open(BytesIO(img_data))
            print("image open")

            image.save("received_frame.jpg")

            print("Frame received and saved")
    except Exception as e:
        print("WebSocket error:", e)
    finally:
        print("Client disconnected")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#run python api.py 