import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models

def send_email_hiring(recipient, employee_name, Department):
    sender_name = "HR Agent"
    company_name = "HR Organization Inc."
    sender_email = "hrorganization.009@gmail.com"
    app_password = "gscojcwjdughkdzp"

    receiver_email = recipient

    smtp_server = "smtp.gmail.com"
    port = 587

   
    body = f"""
Dear {employee_name},

We are pleased to inform you that you have been officially selected to join the {Department} Department at {company_name}.

After reviewing your profile, skills, and performance throughout the evaluation process, we believe that you will be a valuable addition to our team. Your passion for technology and your strong problem-solving abilities stood out clearly.

You will receive a detailed onboarding schedule, along with your initial tasks and team information, within the next few days. Our HR team will also contact you to complete the remaining administrative procedures.

We are excited to welcome you on board and look forward to seeing your contributions in the {Department} Department.

If you have any questions or need further assistance, please feel free to reach out.

Congratulations once again, and welcome to the team!

To finalize your hiring process and prepare your contract, 
please upload your documents (ID, Graduation Cert) via the secure link below:
        
CLICK HERE TO UPLOAD DOCUMENTS:
https://Documents_Form/

Best regards,
{sender_name}
HR Department
{company_name}
"""
# https://Documents_Form/ is not real link, dont use it
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"{Department} Department Acceptance Letter"

    message.attach(MIMEText(body, "plain", "utf-8"))

   
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

def send_email_manager(recipient, employee_name, Manager_Name):
    sender_name = "HR Agent"
    sender_email = "hrorganization.009@gmail.com"
    app_password = "gscojcwjdughkdzp"

    receiver_email = recipient

    smtp_server = "smtp.gmail.com"
    port = 587

   
    body = f"""
Hi {Manager_Name},

I hope you're doing well.

I'm reaching out to inform you that a new employee will be joining your department. Here are the details:

Name: {employee_name}

We are currently finalizing the onboarding process, including required documentation and account setup. Once everything is completed, we will share the onboarding summary with you.

Please prepare any role-specific tasks, access permissions, tools, or equipment the new hire may need during their first week. If you have specific expectations or onboarding steps you want us to include, feel free to send them anytime.

Let me know if you need anything else.
Thanks!

Best regards,
{sender_name}
HR Department
"""

    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "New Team Member Joining Your Department"

    message.attach(MIMEText(body, "plain", "utf-8"))

   
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")



QDRANT_URL = "https://f04ab44d-7efd-4966-8ba7-1e5334332422.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TKp2mJG6GOdU-XaaknAlcC1iDjiKdugLvhDD1C1K9Xk" 

client = QdrantClient(
    url=QDRANT_URL, 
    api_key=QDRANT_API_KEY
)


hiring_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="Status", 
            match=models.MatchValue(value="accepted")
        )
    ]
)


employees, _ = client.scroll(
    collection_name="candidates", 
    scroll_filter=hiring_filter,
    limit=200  
)

for point in employees:
    
    emp_data = point.payload 
    
    emp_name = emp_data.get('first_name')
    emp_email = emp_data.get('email')
    emp_dept = emp_data.get('applied_department')

    
    send_email_hiring(emp_email, emp_name, emp_dept)

    
    dept_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="department_name", 
                match=models.MatchValue(value=emp_dept)
            )
        ]
    )
    
    
    departments, _ = client.scroll(
        collection_name="Departments",
        scroll_filter=dept_filter,
        limit=1
    )
    
    if departments:
        mgr_data = departments[0].payload
        mgr_name = mgr_data.get('manager_name')
        mgr_email = mgr_data.get('manager_email')
        
        
        send_email_manager(mgr_email, emp_name, mgr_name)
