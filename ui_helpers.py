import streamlit as st
from authentication import signup_user, login_user
from streamlit_calendar import calendar


def show_signup_form(users_collection):
    st.header("Sign Up")
    signup_name = st.text_input("Name", key="signup_name")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input(
        "Password", type="password", key="signup_password"
    )
    if st.button("Sign Up"):
        if signup_name and signup_email and signup_password:
            signup_user(
                users_collection, signup_name, signup_email, signup_password
            )
        else:
            st.warning("Please fill in all the fields.")


def show_login_form(users_collection):
    st.header("Log In")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input(
        "Password", type="password", key="login_password"
    )
    if st.button("Log In"):
        if login_email and login_password:
            login_user(users_collection, login_email, login_password)
        else:
            st.warning("Please fill in all the fields.")


from matching import find_match
from datetime import datetime, timedelta
import random
import os
import subprocess
import sys
import urllib.request
import urllib.parse
import requests


def show_main_page(users_collection):
    st.title("✨ Random MeetUp Matcher")
    st.write(
        f"Welcome, {st.session_state['user_name']}! Input your **worries** and **current mood** to be matched with others."
    )

    # User input form for worries and mood
    with st.form("user_input"):
        worries = st.text_input("Your Worries/Problems (comma-separated)")
        mood = st.selectbox(
            "How are you feeling?",
            ["Happy", "Curious", "Anxious", "Excited", "Relaxed"],
        )
        submit_button = st.form_submit_button("Submit")

    # Submit the form to store user data
    if submit_button:
        if worries and mood:
            users_collection.update_one(
                {"email": st.session_state["user_email"]},
                {"$set": {"worries": worries, "mood": mood}},
                upsert=True,
            )
            st.success("Your data has been submitted successfully!")
        else:
            st.warning("Please fill in all the fields.")

    # Add matching process using the `find_match` function
    if st.button("Find Someone to Talk to"):
        matched_user = find_match(users_collection)
        if not matched_user.empty:
            st.write(
                f"🎉 You have been matched with: **{matched_user['user_name']}**"
            )
            st.write(
                f"They're feeling **{matched_user['mood']}** and worried about: **{matched_user['worries']}**"
            )

    # Sending Daily Match Emails:
    if st.button("Daily Match"):
        url = "https://magicloops.dev/api/loop/run/f9d69808-e28c-44b1-b8d1-dc003f263333"
        payload = {
            "match_name": "Johnny",
            "match_preferred_pron": "They/Their",
            "match_mood_today": "hyped",
            "match_personality": "ESTP",
            "match_hobbies": "creative writing",
            "match_education": "college",
            "user_name": "Wendy",
            "user_preferred_pron": "She/Her",
            "user_mood_today": "sad",
            "user_personality": "ISFJ",
            "user_hobbies": "reading novels",
            "user_education": "college",
        }
        response = requests.get(url, json=payload)
        responseJson = response.json()
        st.write("Email sent")

    # mode = "list"
    calendar_resources = []
    cal_events = [
        {
            "title": "Meeting - Anxious",
            "color": "#FF6C6C",
            "start": "2024-09-29",
            "end": "2024-09-29",
            "resourceId": "a",
        },
        {
            "title": "Meeting - Happy",
            "color": "#FF6C6C",
            "start": "2024-09-30",
            "end": "2024-09-30",
            "resourceId": "a",
        },
        {
            "title": "Meeting - Anxious",
            "color": "#FF6C6C",
            "start": "2024-10-03",
            "end": "2024-10-03",
            "resourceId": "a",
        },
    ]

    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "resources": calendar_resources,
        "selectable": "true",
        "initialDate": f"{datetime.now().strftime('%Y-%m-%d')}",
        "initialView": "listMonth",
    }

    count = 1

    cal = calendar(
        events=cal_events,
        options=calendar_options,
        custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
    )

    # Meeting scheduling button and logic
    if st.button("Schedule Meeting"):
        now = datetime.now()
        random_hours = random.randint(1, 24)
        meeting_time = now + timedelta(hours=random_hours)
        meeting_end = meeting_time + timedelta(hours=1)
        meeting_link = f"https://meetup.com/{random.randint(1000, 9999)}"

        st.write(
            f"Your meeting is scheduled at **{meeting_time.strftime('%Y-%m-%d %H:%M:%S')}**"
        )
        st.write(f"[Join Meeting Here]({meeting_link})")

        event = {
            "title": f"Event {count}",
            "color": "#FF6C6C",
            "start": f"{meeting_time.strftime('%Y-%m-%d %H')}",
            "end": f"{meeting_end.strftime('%Y-%m-%d %H')}",
            "resourceId": "a",
        }

        count += 1

        cal_events.append(event)

        # Does not modify the actual calendar.
        # Likely need to store events outside of program (MongoDB, etc)
        # so the events can be pulled everytime the page is reloaded.
        cal["events"] = cal_events
