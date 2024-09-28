import smtplib
from email.mime.text import MIMEText
import streamlit as st
import pandas as pd
import pymongo  # type: ignore
from pymongo import MongoClient
import random
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import secrets
import re
import bcrypt

# MongoDB Connection Setup
MONGO_URI = "mongodb+srv://ambbrown:jFbMJWFY62O62IwO@cluster0.h4lpo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client["meetup_app_db"]
users_collection = db["users"]

# Page configuration
st.set_page_config(page_title="Random MeetUp Matcher", page_icon="✨", layout="centered")

# Initialize session state for authentication and page navigation
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

# **Step 1: Verification Logic** - Placed at the start of the script
query_params = st.experimental_get_query_params()
if 'verify_token' in query_params:
    verify_token = query_params['verify_token'][0]  # Get the token from the query parameter
    user = users_collection.find_one({"verification_token": verify_token})

    if user:
        # Mark the user as verified
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"verified": True}})
        st.success("Your email has been successfully verified! You can now log in.")
        # Redirect to login page
        st.session_state['current_page'] = 'login'
        st.experimental_set_query_params()  # Clear the query parameters
    else:
        st.error("Invalid or expired verification link.")

# Function to sign up users and include email verification with SMTP
def signup_user(name,email, password):
    user = users_collection.find_one({"email": email})
    if user:
        st.error("User already exists! Please log in.")
    else:
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate a unique verification token
        verification_token = secrets.token_urlsafe(16)

        # Store user in the database with a verification token and mark as unverified
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "verified": False,
            "verification_token": verification_token
        })

        # Send a verification email using SMTP
        send_verification_email_smtp(email, verification_token)
        st.success("Successfully signed up! Please check your email to verify your account.")

# Function to login users
def login_user(name, email, password):
    # Find user by email
    user = users_collection.find_one({"email": email})
    if user:
        # Check if the password matches
        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            # Check if the email is verified
            if user.get("verified", False):
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = email
                st.session_state['user_name'] = name
                st.session_state['current_page'] = 'main'
                st.experimental_set_query_params()  # Clear the query parameters
            else:
                st.error("Please verify your email before logging in.")
        else:
            st.error("Invalid password.")
    else:
        st.error("User not found.")

# SMTP Email Verification Function
def send_verification_email_smtp(to_email, token):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "mabrown8888@gmail.com"
    sender_password = "lfhn wrdf zwvz anzu"

    verification_link = f"http://localhost:8501/?verify_token={token}"
    subject = "Verify Your Email Address"
    body = f"Please click the following link to verify your email address: {verification_link}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        st.success("Verification email sent. Please check your inbox.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to validate email format
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Page rendering logic based on current page
if st.session_state['current_page'] == 'login':
    st.title("Welcome to Random MeetUp Matcher!")
    # Tabs for signup and login
    tab1, tab2 = st.tabs(["Sign Up", "Log In"])

    # Signup Form
    with tab1:
        st.header("Sign Up")
        signup_name = st.text_input("Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            if signup_email and signup_password:
                if is_valid_email(signup_email):
                    signup_user(signup_name, signup_email, signup_password)
                else:
                    st.warning("Please enter a valid email address.")
            else:
                st.warning("Please fill in all the fields.")

    # Login Form
    with tab2:
        st.header("Log In")
        # login_name = st.text_input("Name", key="login_name")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_name = st.session_state['signup_name']
        if st.button("Log In"):
            if login_email and login_password:
                login_user(login_name, login_email, login_password)
            else:
                st.warning("Please fill in all the fields.")

elif st.session_state['current_page'] == 'main':
    st.title("✨ Random MeetUp Matcher")
    st.write(f"Welcome, {st.session_state['user_name']}! Input your **interests** and **current mood** to be matched with others.")

    # User input form for interests and mood
    with st.form("user_input"):
        # user_name = st.text_input("Your Name")
        interests = st.text_input("Your Interests (comma-separated)")
        mood = st.selectbox("How are you feeling?", ["Happy", "Curious", "Anxious", "Excited", "Relaxed"])
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if interests and mood:
            users_collection.update_one(
                {"email": st.session_state['user_email']},
                {"$set": {"interests": interests, "mood": mood}},
                upsert=True
            )
            st.success("Your data has been submitted successfully!")
        else:
            st.warning("Please fill in all the fields.")

    # Fetch all users for matching (for demo purposes)
    # st.subheader("Current Users in the System")
    users = list(users_collection.find({}))
    # if users:
    #     for user in users:
    #         st.write(f"User: {user.get('user_name', 'N/A')}, Interests: {user.get('interests', 'N/A')}, Mood: {user.get('mood', 'N/A')}")

    # Matching process
    if st.button("Find a Match"):
        users_df = pd.DataFrame(users)
        if len(users_df) > 1:
            # Vectorize interests for similarity matching
            vectorizer = TfidfVectorizer()
            interests_matrix = vectorizer.fit_transform(users_df['interests'].fillna(''))

            # Calculate similarity
            similarity_matrix = cosine_similarity(interests_matrix)

            # Find closest match for the current user
            current_user_index = users_df[users_df['email'] == st.session_state['user_email']].index[0]
            similarity_scores = similarity_matrix[current_user_index]
            closest_match_index = similarity_scores.argsort()[-2]  # Second highest value for the closest match

            matched_user = users_df.iloc[closest_match_index]
            st.write(f"🎉 You have been matched with: **{matched_user['user_name']}**")
        else:
            st.warning("Not enough users to find a match. Please wait for more participants.")

    # Meeting scheduling
    if st.button("Schedule Meeting"):
        now = datetime.now()
        random_hours = random.randint(1, 24)
        meeting_time = now + timedelta(hours=random_hours)
        meeting_link = f"https://meetup.com/{random.randint(1000, 9999)}"

        st.write(f"Your meeting is scheduled at **{meeting_time.strftime('%Y-%m-%d %H:%M:%S')}**")
        st.write(f"[Join Meeting Here]({meeting_link})")
