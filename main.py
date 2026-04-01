from loguru import logger
import uvicorn
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def read_root():
    logger.info("GET / called")
    return {}


# check
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
