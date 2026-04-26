"""
-------------------------------------------------
   File Name：     ui
   Description :   Streamlit 前端 (修复流式显示)
   Author :        WorldEater2946
   date：          2026/4/26 22:39
-------------------------------------------------
"""
import streamlit as st
import requests
import json

# 后端地址
API_URL = "https://deemo2946-my-chatbot-api.hf.space/api/chat"

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
        st.error("请先在左侧侧边栏输入 API Key！")
        st.stop()

    # 1. 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 准备发送给后端的数据
    history_payload = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    payload = {
        "message": prompt,
        "api_key": api_key,
        "history": history_payload
    }

    # 3. 调用后端并流式显示 (关键修改部分)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # --- 修改开始：加入 st.spinner ---
            with st.spinner("🧠 正在深度思考中..."):
                # 发起流式请求
                with requests.post(API_URL, json=payload, stream=True) as r:
                    if r.status_code == 200:
                        # 逐行处理流式数据
                        for line in r.iter_lines():
                            if line:
                                # 去掉 "data: " 前缀
                                decoded_line = line.decode("utf-8").strip()
                                if decoded_line.startswith("data: "):
                                    data_str = decoded_line[6:]

                                    # 跳过 [DONE] 标记
                                    if data_str == "[DONE]":
                                        continue

                                    try:
                                        # 解析 JSON 数据
                                        data = json.loads(data_str)
                                        content = data.get("content", "")
                                        full_response += content

                                        # 实时更新显示 (加上闪烁光标)
                                        message_placeholder.markdown(full_response + "▌")
                                    except json.JSONDecodeError:
                                        continue
                        # 最终显示 (去掉光标)
                        message_placeholder.markdown(full_response)
                    else:
                        # 处理错误
                        try:
                            error_detail = r.json()
                            st.error(f"❌ 后端错误: {error_detail.get('detail', 'Unknown error')}")
                        except:
                            st.error(f"❌ 连接错误: {r.status_code}")

        except Exception as e:
            st.error(f"❌ 无法连接到后端，请确保 app.py 正在运行: {e}")

    # 4. 保存 AI 回复到历史
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})