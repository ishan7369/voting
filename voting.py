import streamlit as st
import pandas as pd
import json
import os

# File paths for storing user credentials, voting data, and team names
USER_FILE = 'users.json'
VOTES_FILE = 'votes.json'
TEAMS_FILE = 'teams.json'

# Initialize the users, votes, and teams data
def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as f:
                users = json.load(f)
                if not users:  # If file is empty, use default users
                    users = {"admin": "admin123"}
                    save_users(users)  # Save the default user to the file
                return users
        except json.JSONDecodeError:
            # Handle corrupted or empty JSON file
            st.warning("User file is corrupted or empty. Initializing default users.")
            users = {"admin": "admin123"}
            save_users(users)
            return users
    else:
        # If the file doesn't exist, create it and save default users
        users = {"admin": "admin123"}
        save_users(users)
        return users

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def load_votes():
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle corrupted or empty votes file
            st.warning("Votes file is corrupted or empty. Initializing voting data.")
            return {}
    else:
        return {}

def save_votes(votes):
    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f)

def load_teams():
    if os.path.exists(TEAMS_FILE):
        try:
            with open(TEAMS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle corrupted or empty teams file
            st.warning("Teams file is corrupted or empty. Initializing team data.")
            return []
    else:
        return []

def save_teams(teams):
    with open(TEAMS_FILE, 'w') as f:
        json.dump(teams, f)

# Load user, vote, and team data
users = load_users()
votes = load_votes()
teams = load_teams()

# Initialize session state for login and voting
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# Function to authenticate user
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

# Function to register a new user
def register_user(username, password):
    if username not in users:
        users[username] = password
        save_users(users)
        st.success(f"User '{username}' registered successfully!")
    else:
        st.error("Username already exists. Please choose a different username.")

# Function to add a team
def add_team(team_name):
    if team_name not in teams:
        teams.append(team_name)
        save_teams(teams)
        if team_name not in votes:
            votes[team_name] = {"total_votes": 0, "voters": []}
            save_votes(votes)
        st.success(f"Team '{team_name}' added!")
    else:
        st.error(f"Team '{team_name}' already exists!")

# Function to vote for a team
def vote_for_team(team_name, vote_value, username):
    if team_name in votes:
        if isinstance(votes[team_name], dict) and "total_votes" in votes[team_name] and "voters" in votes[team_name]:
            votes[team_name]["total_votes"] += vote_value
            votes[team_name]["voters"].append({"username": username, "vote": vote_value})
            save_votes(votes)
        else:
            votes[team_name] = {"total_votes": vote_value, "voters": [{"username": username, "vote": vote_value}]}
            save_votes(votes)

# Function to delete a team
def delete_team(team_name):
    if team_name in teams:
        teams.remove(team_name)
        save_teams(teams)  # Save the updated team list
        if team_name in votes:
            del votes[team_name]  # Delete votes for the team
            save_votes(votes)  # Save the updated votes data
        st.success(f"Team '{team_name}' and its votes have been deleted!")
    else:
        st.error(f"Team '{team_name}' does not exist!")

# Login form
if not st.session_state['logged_in']:
    st.title("Login or Register")

    choice = st.radio("Select an option", ["Login", "Register"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = username
                st.success("Login successful!")
            else:
                st.error("Invalid credentials. Please try again.")

    if choice == "Register":
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if new_password == confirm_password:
            if st.button("Register"):
                register_user(new_username, new_password)
        else:
            st.error("Passwords do not match.")

# Voting and Results interface (only visible after login)
if st.session_state['logged_in']:
    st.title("Voting App")

    # Add a team
    st.subheader("Add a Team")
    team_name = st.text_input("Enter Team Name:")
    if st.button("Add Team"):
        if team_name:
            add_team(team_name)

    # Delete a team
    st.subheader("Delete a Team")
    if teams:
        team_to_delete = st.selectbox("Select a Team to Delete", teams)
        if st.button("Delete Team"):
            if team_to_delete:
                delete_team(team_to_delete)
    else:
        st.warning("No teams available to delete.")

    # Vote for a team
    st.subheader("Vote for a Team")
    if teams:
        team_choice = st.selectbox("Select a Team to Vote", teams)
        vote_value = st.slider("Select Vote Value (1 to 10)", 1, 10, 1)
        if st.button("Vote"):
            if team_choice:
                vote_for_team(team_choice, vote_value, st.session_state['current_user'])
                st.success(f"Vote of {vote_value} for '{team_choice}' recorded!")
    else:
        st.warning("No teams available to vote for.")

    # Show results button
    if st.button("Show Results"):
        st.subheader("Voting Results")
        if teams:
            result_data = []
            for team, data in votes.items():
                result_data.append([team, data["total_votes"], len(data["voters"])])
            results = pd.DataFrame(result_data, columns=["Team", "Total Votes", "Number of Voters"])
            st.write(results)

            # Show who voted for each team
            st.subheader("Who Voted for Each Team")
            for team, data in votes.items():
                st.write(f"**{team}**:")
                for voter in data["voters"]:
                    st.write(f"- {voter['username']} voted {voter['vote']} points")
        else:
            st.write("No teams have been added yet.")
