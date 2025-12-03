import streamlit as st
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from qdrant_client import QdrantClient
from qdrant_client.http import models
from datetime import datetime

st.set_page_config(page_title="Hiring Portal", page_icon="🏢", layout="centered")

QDRANT_URL = "https://f04ab44d-7efd-4966-8ba7-1e5334332422.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TKp2mJG6GOdU-XaaknAlcC1iDjiKdugLvhDD1C1K9Xk" 

COLLECTION_NAME = "employees" 

UPLOAD_FOLDER = "local_drive_storage"
SENDER_EMAIL = "hrorganization.009@gmail.com"
APP_PASSWORD = "gscojcwjdughkdzp"
TASKS_LINK = "https://Tasks_Platform_Link_Here/" 

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_qdrant_client():
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        return client
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

def check_user_exists(email):
    client = get_qdrant_client()
    if not client: return None
    search_filter = models.Filter(
        must=[models.FieldCondition(key="email", match=models.MatchValue(value=email))]
    )
    records, _ = client.scroll(
        collection_name=COLLECTION_NAME, scroll_filter=search_filter, limit=1, with_payload=True, with_vectors=False
    )
    if records: return records[0] 
    return None

def update_candidate_status(point_id):
    client = get_qdrant_client()
    if not client: return False
    try:
        client.set_payload(
            collection_name=COLLECTION_NAME,
            payload={
                "filled_form": True, 
                "form_completed_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            },
            points=[point_id]
        )
        return True
    except Exception as e:
        st.error(f"Error updating database: {e}")
        return False

def save_uploaded_file(uploaded_file, user_id, user_name):
    if uploaded_file is not None:
        return "dummy_path/file_accepted" 
    return None

def send_task_notification_email(recipient_email, candidate_name):
    sender_name = "HR Team"
    company_name = "HR Organization Inc."
    smtp_server = "smtp.gmail.com"
    port = 587
    body = f"""Dear {candidate_name},\n\nThank you for submitting your documents. Next step: Tasks.\nLink: {TASKS_LINK}\n\nBest,\n{sender_name}"""
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = f"Action Required: Onboarding Tasks for {candidate_name}"
    message.attach(MIMEText(body, "plain", "utf-8"))
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

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

    .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
    }
    .stTextInput label { color: #31333F !important; font-weight: 600 !important; }

    [data-testid='stFileUploader'] {
        background-color: #ffffff;
        border: 1px dashed #4A90E2;
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid='stFileUploader'] section { background-color: #f8f9fa !important; }
    [data-testid='stFileUploader'] div, 
    [data-testid='stFileUploader'] span, 
    [data-testid='stFileUploader'] small { color: #000000 !important; }
    [data-testid='stFileUploader'] button {
        background-color: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #2563eb !important;
        font-weight: 600;
    }
    [data-testid='stFileUploader'] svg { fill: #4A90E2 !important; }

    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #2563eb !important; 
        border: none !important;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        width: 100%;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    .stButton > button *, div[data-testid="stFormSubmitButton"] > button * {
        color: #ffffff !important; 
        font-weight: 600 !important;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #1d4ed8 !important;
    }

    .profile-card {
        background-color: white;
        padding: 20px 20px 10px 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .profile-card h4 { margin-bottom: 10px !important; color: #2563eb !important; }
    .profile-card hr { margin-top: 5px !important; margin-bottom: 15px !important; border-top: 1px solid #eee; }

    div[data-testid="stAlert"] { padding: 10px; border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['logged_in']:
    
    st.markdown("""
    <div class="custom-header">
        <h1>🚀 Hiring Portal</h1>
        <p>Secure Employee Onboarding System</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; margin-top: -50px;">
            <h3 style="color: #333 !important; margin-bottom: 5px;">Welcome Back! 👋</h3>
            <p style="color: #666 !important; font-size: 0.9rem; margin-bottom: 25px;">Please verify your identity to continue</p>
        </div>
        """, unsafe_allow_html=True)
        
        email_input = st.text_input("Email Address", placeholder="e.g., ahmed@example.com", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Verify Identity"):
            if email_input:
                with st.spinner("Wait..."): 
                    user_point = check_user_exists(email_input)
                    if user_point:
                        raw_payload = user_point.payload
                        filled_form_status = str(raw_payload.get("filled_form", "False")).lower().strip()
                        
                        if filled_form_status != "true":
                            st.session_state['logged_in'] = True
                            st.session_state['user_data'] = user_point
                            st.rerun()
                        else:
                            st.warning("✅ You have already submitted your documents.")
                    else:
                        st.error("Email not found in our records.")

else:
    user = st.session_state['user_data']
    user_payload = user.payload
    
    first_name = user_payload.get('first_name', user_payload.get('last_name', 'Candidate'))
    
    st.markdown(f"""
    <div class="custom-header" style="padding: 2rem; border-radius: 0 0 20px 20px; text-align: left; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>Onboarding Dashboard</h1>
            <p>Welcome, {first_name}</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; color: white !important;">
            🟢 Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    main_col1, main_col2 = st.columns([2, 1])

    with main_col1:
        st.markdown("### 📝 Required Documents")
        with st.form("upload_form"):
            st.markdown("#### 1. Personal Verification")
            c1, c2 = st.columns(2)
            with c1: st.text_input("Full Name", value=first_name, disabled=True)
            with c2: st.text_input("Email", value=user_payload.get("email", ""), disabled=True)
            
            st.markdown("---")
            st.markdown("#### 2. Upload Files")
            
            doc_id = st.file_uploader("National ID Scan", type=['jpg', 'png', 'pdf'])
            doc_grad = st.file_uploader("Graduation Certificate", type=['jpg', 'png', 'pdf'])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("✅ Submit & Save Profile")
            
            if submitted:
                if doc_id and doc_grad:
                    with st.spinner("Uploading..."):
                        save_uploaded_file(doc_id, str(user.id), first_name)
                        save_uploaded_file(doc_grad, str(user.id), first_name)
                        if update_candidate_status(user.id):
                            send_task_notification_email(user_payload.get("email"), first_name)
                            st.balloons()
                            st.success("Documents uploaded successfully!")
                            
                            user_payload['filled_form'] = True
                        else:
                            st.error("Database Connection Error")
                else:
                    st.error("Please upload all required documents.")

    with main_col2:
        st.markdown("""
        <div class="profile-card">
            <h4>👤 Your Profile</h4>
            <hr>
            <p><strong>Role:</strong><br>{}</p>
            <p><strong>Department:</strong><br>{}</p>
        </div>
        """.format(user_payload.get('job_title', 'N/A'), user_payload.get('department', 'General')), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state['logged_in'] = False
            st.rerun()