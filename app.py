"""
-------------------------------------------------
   File Name：     app
   Description :   FastAPI 后端 (支持流式输出)
   Author :        WorldEater2946
   date：          2026/4/26 22:32
-------------------------------------------------
"""
# app.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

# 允许跨域
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
        # 1. 初始化 OpenAI 客户端
        client = OpenAI(
            api_key=request.api_key,
            base_url="https://api.deepseek.com"
        )

        # 2. 构建消息列表
        messages = [{"role": "system", "content": "你是一个有帮助的助手。"}]
        messages.extend(request.history)
        messages.append({"role": "user", "content": request.message})

        # 3. 调用 DeepSeek (开启流式)
        # 注意：新版 SDK 这里返回的是同步生成器，但在 FastAPI 异步路由中使用需注意
        # 我们这里改为普通 def 路由，或者在 StreamingResponse 中处理
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )

        # 4. 定义生成器函数 (用于流式响应)
        # 必须按照 SSE (Server-Sent Events) 格式输出: data: {json}\n\n
        def event_generator():
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    # 按 SSE 格式拼接字符串
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False}\n\n"
            # 发送结束标记
            yield "data: [DONE]\n\n"

        # 5. 使用 StreamingResponse 返回
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        # 如果出错，返回普通 JSON 错误
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)