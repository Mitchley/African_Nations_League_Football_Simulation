# African Nations League - Tournament Simulator
## Description

The African Nations League Tournament Simulator is a web application designed to simulate a continental football competition featuring African national teams. The platform provides realistic match simulation, team management, and tournament tracking capabilities for the INF4001N 2025 entrance exam.
Files

    app.py: Main application file containing the Streamlit dashboard

    frontend/utils/: Directory containing authentication, database, and match simulation modules

    requirements.txt: Python dependencies required for the application

# Features

    Multi-role access system (Admin, Federation, Visitor)

    Tournament bracket management with knockout stages

    Realistic match simulation with AI-powered commentary

    Team registration and squad management

    Live tournament tracking and statistics

# Usage

To run the dashboard, execute the following command in your terminal:
bash

# Install required dependencies
pip install streamlit pymongo python-dotenv

# Run the application
streamlit run app.py

Login Credentials

    Admin: username = admin@africanleague.com 
           password = admin123

    Federation: Register with country and team details

    Visitor: Browse tournament without login

# Tournament Rules

    8-team knockout tournament (Quarter-finals → Semi-finals → Final)

    23-player squads with position-based ratings

    Team rating calculated from player averages

    Realistic match simulation using rating-based probability system

# Technical Requirements

    Python 3.8+

    MongoDB database

    Streamlit framework

Developed for INF4001N: 2025 Entrance Exam - African Nations League Simulation
