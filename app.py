import streamlit as st
from authentication import signup_user, login_user, verify_user_token
from ui_helpers import show_signup_form, show_login_form, show_main_page
from database import connect_db

# Page configuration
st.set_page_config(page_title="Random MeetUp Matcher", page_icon="✨", layout="wide")

# Initialize session state for authentication and navigation
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

# Database connection
db = connect_db()
users_collection = db["users"]

# Verification Logic - Verify user's email when the link is clicked
verify_user_token(users_collection)

# Page rendering logic
if st.session_state['current_page'] == 'login':
    st.sidebar.title("Navigation")
    show_signup_form(users_collection)
    show_login_form(users_collection)
elif st.session_state['current_page'] == 'main':
    show_main_page(users_collection)
