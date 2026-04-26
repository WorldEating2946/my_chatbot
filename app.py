"""
-------------------------------------------------
   File Name：     app
   Description :
   Author :        WorldEater2946
   date：          2026/4/26 22:32
-------------------------------------------------
   Change Activity:
                   2026/4/26 22:32:
-------------------------------------------------
"""
# app.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import uvicorn

app = FastAPI()

# 允许跨域（让前端页面能访问后端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求数据模型
class ChatRequest(BaseModel):
    message: str
    api_key: str
    history: Optional[List[dict]] = []

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.api_key:
        raise HTTPException(status_code=400, detail="API Key 不能为空")

    try:
        # 初始化 OpenAI 客户端 (使用用户传来的 Key)
        client = OpenAI(
            api_key=request.api_key,
            base_url="https://api.deepseek.com"
        )

        # 构建消息列表
        messages = [{"role": "system", "content": "你是一个有帮助的助手。"}]
        # 添加历史记录
        messages.extend(request.history)
        # 添加当前问题
        messages.append({"role": "user", "content": request.message})

        # 调用 DeepSeek (开启流式)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        # 生成器：逐块返回数据
        def generate():
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        return {"status": "success", "stream": generate()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)