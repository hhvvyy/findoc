import streamlit as st
import requests

# Define the backend URL where FastAPI is running
FASTAPI_URL = "http://127.0.0.1:8000"

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FinDoc AI", page_icon="📄", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        /* Push the chat input slightly up to make room for the disclaimer */
        [data-testid="stChatInput"] {
            padding-bottom: 30px;
        }
        
        /* Fixed Disclaimer Footer */
        .disclaimer-footer {
            position: fixed;
            bottom: 5px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #7a7a8a;
            z-index: 99999;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            text-align: center;
            width: 100%;
            pointer-events: none;
        }
        
        /* Premium button styling */
        div.stButton > button:first-child {
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }
        
        /* Welcome box styling */
        .welcome-box {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 20px;
        }
    </style>
    
    <div class='disclaimer-footer'>FinDoc is an AI and can make mistakes. Always verify critical financial data.</div>
""", unsafe_allow_html=True)

# --- STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_audit" not in st.session_state:
    st.session_state.latest_audit = None

# --- SIDEBAR: INGESTION & AUDIT TRAIL ---
with st.sidebar:
    st.title("📄 FinDoc Intelligence")
    
    # Professional tool description
    st.markdown("""
    **Enterprise-grade document analytics.**
    Securely ingest financial reports to extract verified, ground-truth insights via RAG.
    """)
    st.divider()
    
    st.subheader("1. Workspace Setup")
    uploaded_file = st.file_uploader("Upload Financial Document (PDF)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process & Vectorize Document", use_container_width=True):
            with st.spinner("Extracting text and generating embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{FASTAPI_URL}/upload-pdf/", files=files)
                    if response.status_code == 200:
                        st.success("✅ Document successfully indexed and ready for querying.")
                    else:
                        st.error(f"Backend Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to FastAPI server. Ensure backend is running.")
    
    st.divider()
    
    # --- NEW: LIVE AUDIT TRAIL ---
    st.subheader("🔍 Live Audit Trail")
    st.caption("Real-time verification of the most recent AI response.")
    
    if st.session_state.latest_audit:
        audit_status = st.session_state.latest_audit.get("status")
        audit_reasoning = st.session_state.latest_audit.get("reasoning", "No reasoning provided.")
        
        if audit_status == "PASSED":
            st.success("🟢 **Status: Verified Grounded**\n\n100% backed by document context.")
        else:
            st.warning("⚠️ **Status: Confidence Warning**\n\nDetected potentially unsupported claims.")
            
        with st.expander("View Judge's Step-by-Step Reasoning"):
            st.markdown(audit_reasoning)
    else:
        st.info("Ask a question to see the evaluator's analysis here.")

    st.divider()
    with st.expander("⚙️ System Capabilities & Limitations", expanded=False):
        st.markdown("""
        - **Supported Formats:** `.pdf` only.
        - **Data Privacy:** Documents are processed in-memory.
        - **Hallucination Check:** An automated judge evaluates all AI responses.
        """)

# --- MAIN CHAT INTERFACE ---
st.title("Analytical Interface")

# --- EMPTY STATE / ONBOARDING ---
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="welcome-box">
            <h3>Welcome to your Document Sandbox</h3>
            <p>Upload a document in the sidebar to begin. Once processed, you can ask complex analytical questions such as:</p>
            <ul>
                <li><em>"Summarize the key risk factors mentioned in the Annual Report."</em></li>
                <li><em>"What is the total revenue reported for Q3, and how does it compare to operating expenses?"</em></li>
                <li><em>"Extract all mentions of regulatory compliance."</em></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Display previous chat messages (Clean text only)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_question := st.chat_input("Query your financial document..."):
    
    # Render user message
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing document vectors..."):
            try:
                payload = {"question": user_question}
                response = requests.post(f"{FASTAPI_URL}/ask", json=payload)
                
                if response.status_code == 200:
                    response_data = response.json()
                    ai_answer = response_data.get("answer")
                    
                    # Ensure your FastAPI backend is now returning "reasoning" in the JSON!
                    audit_status = response_data.get("status")
                    audit_reasoning = response_data.get("reasoning", "No reasoning returned from backend.")
                    
                    # 1. Render clean Answer in chat
                    st.markdown(ai_answer)
                    
                    # 2. Save chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ai_answer
                    })
                    
                    # 3. Update the Audit State and force a sidebar refresh
                    st.session_state.latest_audit = {
                        "status": audit_status,
                        "reasoning": audit_reasoning
                    }
                    st.rerun() # This instantly refreshes the UI so the sidebar updates
                    
                else:
                    st.error(f"Error from server: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI server. Please check your backend connection.")