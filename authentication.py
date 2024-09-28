import bcrypt
import streamlit as st
from email_service import send_verification_email
import secrets

def signup_user(users_collection, name, email, password):
    # User creation logic
    user = users_collection.find_one({"email": email})
    if user:
        st.error("User already exists! Please log in.")
    else:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        verification_token = secrets.token_urlsafe(16)
        users_collection.insert_one({
            "user_name": name,
            "email": email,
            "password": hashed_password,
            "verified": False,
            "verification_token": verification_token
        })
        send_verification_email(email, verification_token)
        st.success("Successfully signed up! Please check your email to verify your account.")

def login_user(users_collection, email, password):
    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        if user.get("verified", False):
            st.session_state['authenticated'] = True
            st.session_state['user_email'] = email
            st.session_state['user_name'] = user["user_name"]
            st.session_state['current_page'] = 'main'
            st.query_params = {}
            # st.experimental_rerun()
        else:
            st.error("Please verify your email before logging in.")
    else:
        st.error("Invalid email or password.")

def verify_user_token(users_collection):
    query_params = st.query_params  # Use the updated query parameter function
    if 'verify_token' in query_params:
        token = query_params['verify_token']
        if token:  # Check if the token is present
            token = token[0]  # Extract the token from the list
            user = users_collection.find_one({"verification_token": token})
            if user:
                users_collection.update_one({"_id": user["_id"]}, {"$set": {"verified": True}})
                st.success("Your email has been successfully verified! You can now log in.")
                st.session_state['current_page'] = 'login'
                # Clear the query parameters after successful verification
                st.query_params = {}
            else:
                st.error("Invalid or expired verification link.")

