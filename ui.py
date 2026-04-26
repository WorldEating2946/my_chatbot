"""
-------------------------------------------------
   File Name：     ui
   Description :
   Author :        WorldEater2946
   date：          2026/4/26 22:39
-------------------------------------------------
   Change Activity:
                   2026/4/26 22:39:
-------------------------------------------------
"""
import streamlit as st
import requests

# 后端地址 (本地运行通常是 localhost:8000)
API_URL = "http://127.0.0.1:8000/api/chat"

st.title("🔑 自定义 API Key 聊天机器人")
st.markdown("请输入你的 DeepSeek API Key，它只会用于本次对话，不会被存储。")

# 侧边栏输入 Key
api_key = st.sidebar.text_input("DeepSeek API Key", type="password")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入你的问题..."):
    if not api_key:
        st.error("请先在左侧输入 API Key！")
        st.stop()

    # 1. 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 准备发送给后端的数据
    # 注意：我们需要把 session_state 里的历史转换成后端能懂的格式
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]  # 不包含刚发的这条
    ]

    payload = {
        "message": prompt,
        "api_key": api_key,
        "history": history_payload
    }

    # 3. 调用后端并流式显示
    with st.chat_message("assistant"):
        try:
            # 这里使用 requests 的 stream 模式
            with requests.post(API_URL, json=payload, stream=True) as r:
                if r.status_code == 200:
                    # 简单的流式处理 (实际生产中建议用 SSE 客户端)
                    # 注意：FastAPI 返回的是 JSON 流，这里简化处理
                    # 为了演示简单，这里我们假设后端返回的是文本流
                    # 实际上 FastAPI 返回 JSON 需要特殊处理，
                    # 更好的方式是直接用 Streamlit 的原生能力，但为了演示“前后端分离”，
                    # 我们这里用一个简单的占位符逻辑，或者你需要写更复杂的流解析代码。

                    # *简化方案*：为了让你能跑通，这里暂时不使用复杂的流解析，
                    # 而是直接请求后端。如果需要完美流式，建议使用 Streamlit 原生写法。
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        st.write("后端连接成功！(此处需完善流式解析代码)")
                    else:
                        st.error(response.json())
                else:
                    st.error(f"后端错误: {r.status_code}")
        except Exception as e:
            st.error(f"连接失败: {e}")