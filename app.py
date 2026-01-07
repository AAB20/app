import streamlit as st
import ollama
import os
import json
from datetime import datetime
import extra_streamlit_components as stx # مكتبة الكوكيز

# --- 1. إعدادات النظام ---
MODEL_NAME = "akinyurt5"
HISTORY_DIR = "chat_history"

if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# --- 2. إدارة الكوكيز (Cookies) ---
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# مثال: حفظ تاريخ آخر زيارة في الكوكيز
last_visit = cookie_manager.get(cookie="last_visit")
cookie_manager.set("last_visit", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), expires_at=datetime.now())

# --- 3. واجهة المستخدم (تعديل اللون للأبيض) ---
st.set_page_config(page_title="Akın Yurt AI", page_icon="", layout="wide")

st.markdown(f"""
    <style>
    /* جعل خلفية التطبيق داكنة والنصوص بيضاء */
    .stApp {{ background-color: #343541; color: #ffffff; }}

    /* جعل نصوص الرسائل تظهر باللون الأبيض الصريح */
    .stMarkdown p {{ color: #ffffff !important; font-size: 18px; }}

    /* تنسيق فقاعات الدردشة */
    .stChatMessage {{ border-radius: 8px; margin-bottom: 10px; color: #ffffff; }}
    .stChatMessage[data-testimonial="assistant"] {{ background-color: #444654; border: 1px solid #565869; }}

    .stChatInputContainer {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 65%; z-index: 1000; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. الشريط الجانبي ---
with st.sidebar:
    st.title(" Akın Yurt AI")
    if last_visit:
        st.write(f"Welcome back! Last visit: {last_visit}")

    if st.button(" New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. منطق الدردشة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Akın Yurt..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            stream = ollama.chat(model=MODEL_NAME, messages=st.session_state.messages, stream=True)
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                # إظهار النص باللون الأبيض أثناء الكتابة
                response_placeholder.markdown(f'<p style="color:white;">{full_response}</p>', unsafe_allow_html=True)

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error: {e}")
