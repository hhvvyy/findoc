import streamlit as st
import requests

# Define the backend URL where FastAPI is running
FASTAPI_URL = "http://127.0.0.1:8000"

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FinDoc AI", page_icon="📄", layout="wide")

# --- CUSTOM CSS ---
# 1. Pins the disclaimer under the chat bar
# 2. Adjusts padding to make room for it
# 3. Softens buttons and chat elements for a premium feel
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
            pointer-events: none; /* Allows clicking through if needed */
        }
        
        /* Premium button styling */
        div.stButton > button:first-child {
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }
        
        /* Badge styling */
        .stAlert {
            margin-top: -15px;
            margin-bottom: 15px;
            border-radius: 6px;
            padding: 10px;
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
    
    <!-- Inject Disclaimer HTML immediately -->
    <div class='disclaimer-footer'>FinDoc is an AI and can make mistakes. Always verify critical financial data.</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: INGESTION & INFO ---
with st.sidebar:
    st.title("📄 FinDoc Intelligence")
    
    # Professional tool description
    st.markdown("""
    **Enterprise-grade document analytics.**
    Securely ingest financial reports, filings, and statements to extract verified, ground-truth insights via Retrieval-Augmented Generation (RAG).
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
    
    # Extra UI Element: Capabilities Expander
    with st.expander("⚙️ System Capabilities & Limitations", expanded=False):
        st.markdown("""
        - **Supported Formats:** `.pdf` only.
        - **Data Privacy:** Documents are processed in-memory and embedded locally.
        - **Hallucination Check:** An automated judge evaluates all AI responses against the raw PDF text to ensure accuracy.
        """)

# --- MAIN CHAT INTERFACE ---
st.title("Analytical Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EMPTY STATE / ONBOARDING ---
# Fills the empty space shown in your image before the user starts chatting
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

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Persistent Verification Badge
        if "status" in message:
            if message["status"] == "PASSED":
                st.success("🟢 **Verified Grounded:** Source matched. 100% backed by document context.")
            elif message["status"] == "FAILED":
                st.warning("⚠️ **Confidence Warning:** The auditing judge detected potentially unsupported claims.")

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
                    audit_status = response_data.get("status")
                    
                    # Render Answer
                    st.markdown(ai_answer)
                    
                    # Render Verification Badge
                    if audit_status == "PASSED":
                        st.success("🟢 **Verified Grounded:** Source matched. 100% backed by document context.")
                    else:
                        st.warning("⚠️ **Confidence Warning:** The auditing judge detected potentially unsupported claims.")
                    
                    # Save to state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": ai_answer,
                        "status": audit_status
                    })
                else:
                    st.error(f"Error from server: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI server. Please check your backend connection.")