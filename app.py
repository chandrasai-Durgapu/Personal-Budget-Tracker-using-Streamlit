import streamlit as st
import bcrypt

from setup.db import initialize_database, authenticate_user, create_user, set_default_categories

def login_form():
    st.subheader("Login to your Account")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user['id']
                st.session_state.username = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")

def registration_form():
    st.subheader("Create a New Account")
    with st.form("registration_form"):
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            try:
                user_id = create_user(new_username, new_password)
                set_default_categories(user_id)
                st.success("Account created successfully! You can now log in.")
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = new_username
            except Exception as e:
                st.error(f"Could not create account: {e}")

def main():
    st.set_page_config(
        page_title="Budget Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    initialize_database()

    st.sidebar.title("Navigation")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        st.sidebar.write(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            del st.session_state.user_id
            del st.session_state.username
            
    st.title("Welcome to your Budget Tracker")
    st.markdown("Use the navigation panel on the left to get started.")

    if not st.session_state.logged_in:
        st.info("Please log in or register to use the application.")
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_form()
        with tab2:
            registration_form()
    else:
        st.success("You are logged in. Use the sidebar to navigate to other pages.")

if __name__ == "__main__":
    main()