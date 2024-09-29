import streamlit as st
from authentication import signup_user, login_user
# from streamlit_calendar import calendar

def show_signup_form(users_collection):
    st.header("Sign Up")
    signup_name = st.text_input("Name", key="signup_name")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        if signup_name and signup_email and signup_password:
            signup_user(users_collection, signup_name, signup_email, signup_password)
        else:
            st.warning("Please fill in all the fields.")

def show_login_form(users_collection):
    st.header("Log In")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Log In"):
        if login_email and login_password:
            login_user(users_collection, login_email, login_password)
        else:
            st.warning("Please fill in all the fields.")

from matching import find_match
import streamlit as st
from datetime import datetime, timedelta
import random

def show_main_page(users_collection):
    st.title("✨ Random MeetUp Matcher")
    st.write(f"Welcome, {st.session_state['user_name']}! Input your **worries** and **current mood** to be matched with others.")

    # User input form for worries and mood
    with st.form("user_input"):
        worries = st.text_input("Your Worries/Problems (comma-separated)")
        mood = st.selectbox("How are you feeling?", ["Happy", "Curious", "Anxious", "Excited", "Relaxed"])
        submit_button = st.form_submit_button("Submit")

    # Submit the form to store user data
    if submit_button:
        if worries and mood:
            users_collection.update_one(
                {"email": st.session_state['user_email']},
                {"$set": {"worries": worries, "mood": mood}},
                upsert=True
            )
            st.success("Your data has been submitted successfully!")
        else:
            st.warning("Please fill in all the fields.")

    # Add matching process using the `find_match` function
    if st.button("Find Someone to Talk to"):
        matched_user = find_match(users_collection)
        if not matched_user.empty:
            st.write(f"🎉 You have been matched with: **{matched_user['user_name']}**")
            st.write(f"They're feeling **{matched_user['mood']}** and worried about: **{matched_user['worries']}**")

    # Meeting scheduling button and logic
    if st.button("Schedule Meeting"):
        now = datetime.now()
        random_hours = random.randint(1, 24)
        meeting_time = now + timedelta(hours=random_hours)
        meeting_link = f"https://meetup.com/{random.randint(1000, 9999)}"

        st.write(f"Your meeting is scheduled at **{meeting_time.strftime('%Y-%m-%d %H:%M:%S')}**")
        st.write(f"[Join Meeting Here]({meeting_link})")

