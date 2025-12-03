import streamlit as st
import pandas as pd
import re
import time
from agent import CustomerSupportAgent

st.set_page_config(page_title="H-002 | Enterprise AI Agent", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def get_agent():
    return CustomerSupportAgent()

agent = get_agent()

if "messages" not in st.session_state: st.session_state.messages = []
if "pending_response" not in st.session_state: st.session_state.pending_response = None

# --- SIDEBAR ---
st.sidebar.title("⚙️ Command Center")
st.sidebar.subheader("🔒 Admin Controls")
safety_mode = st.sidebar.toggle("Require Manager Approval", value=False)
st.sidebar.markdown("---")
st.sidebar.subheader("🗂️ Audit & Compliance")
chat_log = "TRANSCRIPT LOG\n"
for msg in st.session_state.messages: chat_log += f"[{msg['role']}]: {msg['content']}\n"
st.sidebar.download_button("Download Logs", chat_log, "audit.txt")

# --- CHAT ---
st.title("🛍️ H-002 | Customer Experience Agent")
st.caption("Try asking: **'Is there a Starbucks in Mumbai?'** or **'I want a refund'**")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- PENDING APPROVAL ---
if st.session_state.pending_response:
    with st.chat_message("assistant"):
        st.warning(f"🔒 **BLOCKED FOR REVIEW**\n\n{st.session_state.pending_response}")
        col1, col2 = st.columns([1,5])
        if col1.button("Approve"):
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.pending_response})
            st.session_state.pending_response = None
            st.rerun()
        if col2.button("Reject"):
            st.session_state.pending_response = None
            st.rerun()

# --- INPUT ---
if not st.session_state.pending_response:
    if prompt := st.chat_input("Type your query..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("🤖 AI Processing..."):
            time.sleep(0.5)
            result = agent.process_request(prompt)

        if safety_mode:
            st.session_state.pending_response = result['response']
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": result['response']})
            with st.chat_message("assistant"):
                st.markdown(result['response'])
                # Map Logic
                map_data = []
                for log in result["logs"]:
                    matches = re.findall(r"Coordinates:\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)", log)
                    for lat, lon in matches: map_data.append({"lat": float(lat), "lon": float(lon)})
                
                # Only show map if response confirms location
                if map_data and "Here is what I found" in result['response']:
                    st.success(f"🗺️ Visualizing {len(map_data)} geospatial points.")
                    st.map(pd.DataFrame(map_data), zoom=12, color='#00ff00')

        # Logs
        st.sidebar.markdown("---")
        st.sidebar.subheader("📝 Live Logs")
        for log in result["logs"]:
            if "SECURITY" in log: st.sidebar.error(log)
            elif "RAG" in log: st.sidebar.info(log[:60]+"...")
            else: st.sidebar.text(log[:60]+"...")