import smtplib
from email.mime.text import MIMEText
import streamlit as st
from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD

def send_verification_email(to_email, token):
    verification_link = f"http://localhost:8501/?verify_token={token}"
    subject = "Verify Your Email Address"
    body = f"Please click the following link to verify your email address: {verification_link}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        st.success("Verification email sent. Please check your inbox.")
    except Exception as e:
        st.error(f"Error sending email: {e}")
