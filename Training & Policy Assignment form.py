import streamlit as st
import os
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from qdrant_client import QdrantClient
from qdrant_client.http import models
from datetime import datetime

st.set_page_config(page_title="DEPI Documents Center", page_icon="📂", layout="centered")

QDRANT_URL = "https://f04ab44d-7efd-4966-8ba7-1e5334332422.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TKp2mJG6GOdU-XaaknAlcC1iDjiKdugLvhDD1C1K9Xk" 

COLLECTION_NAME = "employees" 
SENDER_EMAIL = "hrorganization.009@gmail.com"
APP_PASSWORD = "gscojcwjdughkdzp"

st.markdown("""
<style>
    html, body, [class*="css"], .stMarkdown, h1, h2, h3, h4, h5, h6, p, li, span, label, div {
        color: #31333F;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #f0f2f5; }

    .custom-header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        padding: 2.5rem 1rem;
        text-align: center;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .custom-header h1, .custom-header p, .custom-header div { color: white !important; }
    .custom-header h1 { margin: 0; font-size: 2.5rem; font-weight: 700; }
    .custom-header p { opacity: 0.9; font-size: 1.1rem; margin-top: 10px; }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        margin-top: 1rem !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white !important;
    }

    .stDownloadButton > button {
        background-color: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #2563eb !important;
        border-radius: 8px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover {
        background-color: #f0f9ff !important;
        box-shadow: 0 2px 5px rgba(37, 99, 235, 0.1);
    }
   
    .stDownloadButton > button * {
        color: #2563eb !important;
    }

    div[data-testid="stFormSubmitButton"] > button, .stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        width: 100%;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    .stButton > button p { color: white !important; }
    .stButton > button:hover { background-color: #1d4ed8 !important; }

    .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px;
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def get_qdrant_client():
    try:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    except Exception:
        return None

def check_user_exists(email):
    client = get_qdrant_client()
    if not client: return None
    try:
        search_filter = models.Filter(must=[models.FieldCondition(key="email", match=models.MatchValue(value=email))])
        records, _ = client.scroll(collection_name=COLLECTION_NAME, scroll_filter=search_filter, limit=1, with_payload=True)
        if records: return records[0]
    except: pass
    return None

def update_module_status(point_id):
    client = get_qdrant_client()
    if not client: return False
    try:
        client.set_payload(
            collection_name=COLLECTION_NAME,
            payload={"finished_modules": True, "modules_completed_at": str(datetime.now())},
            points=[point_id]
        )
        return True
    except: return False

def send_completion_email(recipient_email, candidate_name):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = "Welcome Aboard!"
        body = f"Dear {candidate_name},\n\nCongratulations! You have completed the onboarding process.\n\nBest,\nHR Team"
        msg.attach(MIMEText(body, "plain", "utf-8"))
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=ctx)
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        return True
    except: return False

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['logged_in']:
    st.markdown("""
    <div class="custom-header">
        <h1>📂 DEPI Documents Center</h1>
        <p>Review and Sign Company Policies</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; margin-top: -50px;">
            <h3 style="color: #333 !important; margin-bottom: 5px;">Employee Access 👋</h3>
            <p style="color: #666 !important; font-size: 0.9rem; margin-bottom: 25px;">Enter your email to access documents</p>
        </div>
        """, unsafe_allow_html=True)
        
        email_input = st.text_input("Email Address", placeholder="e.g., ahmed@example.com", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Access Portal"):
            if email_input:
                with st.spinner("Checking..."):
                    user_point = check_user_exists(email_input)
                    if user_point:
                        payload = user_point.payload
                        filled = str(payload.get("filled_form", "false")).lower().strip()
                        finished = str(payload.get("finished_modules", "false")).lower().strip()
                        
                        if filled != "true":
                            st.error("⛔ Access Denied: Upload documents first.")
                        elif finished == "true":
                            st.info("✅ You have already finished onboarding.")
                        else:
                            st.session_state['logged_in'] = True
                            st.session_state['user_data'] = user_point
                            st.rerun()
                    else:
                        st.error("Email not found.")
else:
    user = st.session_state['user_data']
    name = user.payload.get('first_name', 'Employee')
    role = user.payload.get('job_title', 'General')

    st.markdown(f"""
    <div class="custom-header" style="padding: 2rem; border-radius: 0 0 20px 20px; text-align: left; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>Documents Dashboard</h1>
            <p>Welcome, {name}</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; color: white !important;">
            📄 Pending Signature
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ⚠️ Please download, read, and acknowledge:")
        st.markdown("---")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.download_button("📥 Download Policy", "Policy Content...", "Policy.txt", key="d1")
        with c2:
            st.write("**1. General Company Policy**")
            ch1 = st.checkbox("I agree to the Policy.", key="c1")

        st.markdown("---")

        c3, c4 = st.columns([1, 2])
        with c3:
            st.download_button("📥 Download Guide", "Guide Content...", "Guide.txt", key="d2")
        with c4:
            st.write(f"**2. {role} Guide**")
            ch2 = st.checkbox(f"I have read the document.", key="c2")
        
        st.markdown("---")
        
        if st.button("✅ Submit Acknowledgments"):
            if ch1 and ch2:
                with st.spinner("Signing..."):
                    time.sleep(1)
                    if update_module_status(user.id):
                        send_completion_email(user.payload.get("email"), name)
                        st.balloons()
                        st.success("All done! Welcome to the team.")
                        time.sleep(3)
                        st.session_state['logged_in'] = False
                        st.rerun()
                    else:
                        st.error("Error saving data.")
            else:
                st.warning("Please check both boxes.")

    if st.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()