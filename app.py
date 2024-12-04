import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random
from streamlit_option_menu import option_menu
from streamlit_calendar import calendar
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
import hydralit_components as hc
from streamlit_card import card

# Set page config
st.set_page_config(
    page_title="TB MedTracker",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state variables
if 'medications' not in st.session_state:
    # Sample medications with TB treatment regimen
    st.session_state.medications = [
        {
            'name': 'Isoniazid (INH)',
            'dosage': '300mg',
            'frequency': 'Once daily',
            'instructions': 'Take on empty stomach',
            'stock': 45,
            'refill_threshold': 10,
            'category': 'TB First-line',
            'next_dose': '08:00'
        },
        {
            'name': 'Rifampin (RIF)',
            'dosage': '600mg',
            'frequency': 'Once daily',
            'instructions': 'Take 1 hour before meals',
            'stock': 60,
            'refill_threshold': 15,
            'category': 'TB First-line',
            'next_dose': '08:00'
        },
        {
            'name': 'Pyrazinamide (PZA)',
            'dosage': '1500mg',
            'frequency': 'Once daily',
            'instructions': 'Take with food',
            'stock': 40,
            'refill_threshold': 10,
            'category': 'TB First-line',
            'next_dose': '08:00'
        },
        {
            'name': 'Ethambutol (EMB)',
            'dosage': '1200mg',
            'frequency': 'Once daily',
            'instructions': 'Take with water',
            'stock': 35,
            'refill_threshold': 10,
            'category': 'TB First-line',
            'next_dose': '08:00'
        }
    ]

if 'reminders' not in st.session_state:
    # Generate sample reminders for the next week
    st.session_state.reminders = []
    for i in range(7):
        for med in st.session_state.medications:
            if med['frequency'] == 'Once daily':
                times = [9]
            elif med['frequency'] == 'Twice daily':
                times = [9, 21]
            else:
                times = [9, 14, 21]
            
            for hour in times:
                reminder_time = datetime.now() + timedelta(days=i, hours=hour-datetime.now().hour)
                st.session_state.reminders.append({
                    'medication': med['name'],
                    'datetime': reminder_time.isoformat(),
                    'note': f'Regular dose of {med["name"]}'
                })

if 'doses_log' not in st.session_state:
    # Generate 6 months of sample dose logs
    st.session_state.doses_log = []
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(180):
        current_date = start_date + timedelta(days=i)
        for med in st.session_state.medications:
            # Simulate realistic medication adherence (85% adherence rate)
            if random.random() < 0.85:
                status = 'Taken'
            elif random.random() < 0.5:
                status = 'Missed'
            else:
                status = 'Delayed'
                
            st.session_state.doses_log.append({
                'medication': med['name'],
                'date': current_date.date().isoformat(),
                'status': status,
                'notes': ''
            })

if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {
        'name': 'John Doe',
        'age': '45',
        'address': '123 Health St, Medical City, MC 12345',
        'emergency_contact': 'Jane Doe (555) 123-4567'
    }

if 'drone_status' not in st.session_state:
    st.session_state.drone_status = 'Available'

if 'drone_location' not in st.session_state:
    st.session_state.drone_location = 'Kitchen'

if 'notifications' not in st.session_state:
    st.session_state.notifications = [
        {'type': 'warning', 'message': 'Isoniazid (INH) stock is running low. Consider refilling soon.'},
        {'type': 'info', 'message': 'Drone is ready to deliver medications from kitchen to bedroom.'},
        {'type': 'success', 'message': 'Perfect medication adherence streak: 7 days!'}
    ]

# Sidebar with modern theme
with st.sidebar:
    # Profile summary card
    with st.container():
        st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
        st.markdown(f"### {st.session_state.personal_info['name']}")
        st.markdown("🏥 Patient ID: #12345")
    
    # Modern navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Analytics", "Personal Info", "Medications", "Schedule", "Drone Service"],
        icons=['house', 'graph-up', 'person', 'capsule', 'calendar', 'robot'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important"},
            "icon": {"font-size": "1rem"}, 
            "nav-link": {
                "font-size": "0.9rem",
                "text-align": "left",
                "margin": "0.5rem 0",
                "--hover-color": "#eee",
            },
        }
    )

# Notification Center
notifications = [n for n in st.session_state.notifications]
if notifications:
    with st.container():
        for notif in notifications:
            if notif['type'] == 'warning':
                color = '#FF4B4B'
            elif notif['type'] == 'info':
                color = '#1E88E5'
            else:
                color = '#4CAF50'
                
            hc.info_card(
                title='',
                content=notif['message'],
                sentiment='good' if notif['type'] == 'success' else 'warning' if notif['type'] == 'warning' else 'neutral',
                bar_value=100,
                key=f"notif_{notifications.index(notif)}"
            )

# Dashboard
if selected == "Dashboard":
    st.title("📊 MedTracker Dashboard")
    
    # Next Medication Countdown
    st.markdown("### ⏰ Next Medication Due")
    now = datetime.now()
    next_med = None
    time_until_next = None
    
    for med in st.session_state.medications:
        next_dose_time = datetime.strptime(med['next_dose'], '%H:%M').time()
        next_dose_datetime = datetime.combine(now.date(), next_dose_time)
        
        if next_dose_datetime < now:
            # If the time has passed today, schedule for tomorrow
            next_dose_datetime = datetime.combine(now.date() + timedelta(days=1), next_dose_time)
        
        if time_until_next is None or (next_dose_datetime - now) < time_until_next:
            time_until_next = next_dose_datetime - now
            next_med = med
    
    if next_med:
        col1, col2 = st.columns([1, 2])
        with col1:
            hours = int(time_until_next.total_seconds() // 3600)
            minutes = int((time_until_next.total_seconds() % 3600) // 60)
            
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h1 style='font-size: 2.5em; margin: 0;'>{hours:02d}:{minutes:02d}</h1>
                <p style='margin: 5px 0;'>hours until next dose</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h3 style='margin: 0;'>{next_med['name']}</h3>
                <p style='margin: 5px 0;'>Dosage: {next_med['dosage']}</p>
                <p style='margin: 5px 0;'>{next_med['instructions']}</p>
                <p style='margin: 5px 0;'>Due at: {next_med['next_dose']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick Stats in modern cards
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            hc.info_card(
                title="Active Medications",
                content=str(len(st.session_state.medications)),
                sentiment='good',
                bar_value=len(st.session_state.medications) * 10
            )
        
        with col2:
            today_doses = len([d for d in st.session_state.doses_log if d['date'] == datetime.now().date().isoformat()])
            hc.info_card(
                title="Today's Doses",
                content=str(today_doses),
                sentiment='good' if today_doses > 0 else 'neutral',
                bar_value=today_doses * 20
            )
        
        with col3:
            adherence_rate = len([d for d in st.session_state.doses_log if d['status'] == 'Taken']) / len(st.session_state.doses_log) * 100
            hc.info_card(
                title="Adherence Rate",
                content=f"{adherence_rate:.1f}%",
                sentiment='good' if adherence_rate > 80 else 'neutral',
                bar_value=adherence_rate
            )
        
        with col4:
            hc.info_card(
                title="Drone Status",
                content=st.session_state.drone_status,
                sentiment='good' if st.session_state.drone_status == 'Available' else 'warning',
                bar_value=100 if st.session_state.drone_status == 'Available' else 50
            )

    # Medication Stock Alerts
    st.markdown("### 📦 Inventory Status")
    stock_cols = st.columns(3)
    for idx, med in enumerate(st.session_state.medications):
        with stock_cols[idx % 3]:
            stock_percent = (med['stock'] / med['refill_threshold']) * 100
            sentiment = 'good' if stock_percent > 200 else 'warning' if stock_percent > 100 else 'poor'
            
            hc.info_card(
                title=med['name'],
                content=f"{med['stock']} pills remaining",
                sentiment=sentiment,
                bar_value=min(stock_percent, 100)
            )

    # Today's Schedule Timeline
    st.markdown("### 📅 Today's Schedule")
    today_reminders = [r for r in st.session_state.reminders 
                      if datetime.fromisoformat(r['datetime']).date() == datetime.now().date()]
    
    for reminder in sorted(today_reminders, key=lambda x: x['datetime'])[:5]:
        reminder_time = datetime.fromisoformat(reminder['datetime'])
        is_past = reminder_time < datetime.now()
        
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### {reminder_time.strftime('%I:%M %p')}")
            with col2:
                if is_past:
                    st.markdown(f"~~{reminder['medication']}: {reminder['note']}~~")
                else:
                    st.markdown(f"**{reminder['medication']}**: {reminder['note']}")

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("💊 Log New Dose", use_container_width=True):
            st.session_state.quick_log = True
    
    with quick_col2:
        if st.button("🔄 Request Refill", use_container_width=True):
            st.success("Refill request sent to pharmacy!")
    
    with quick_col3:
        if st.button("👨‍⚕️ Contact Doctor", use_container_width=True):
            st.info("Opening messaging interface...")

elif selected == "Analytics":
    st.title("📈 Advanced Analytics")
    
    # Time period selector with tabs
    time_options = ["Last 7 Days", "Last 30 Days", "Last 6 Months"]
    time_period = st.radio("Select Time Period", time_options, horizontal=True)
    
    if time_period == "Last 7 Days":
        date_filter = datetime.now().date() - timedelta(days=7)
    elif time_period == "Last 30 Days":
        date_filter = datetime.now().date() - timedelta(days=30)
    else:
        date_filter = datetime.now().date() - timedelta(days=180)
    
    # Initialize doses_log if empty
    if 'doses_log' not in st.session_state:
        st.session_state.doses_log = []
    
    # Sample data generation for analytics
    if len(st.session_state.doses_log) == 0:
        # Generate sample data if no real data exists
        dates = pd.date_range(date_filter, datetime.now().date(), freq='D')
        sample_data = []
        for date in dates:
            for med in st.session_state.medications:
                # Morning dose
                morning_hour = random.randint(6, 9)
                status = random.choices(['Taken', 'Missed', 'Delayed'], weights=[0.85, 0.1, 0.05])[0]
                sample_data.append({
                    'date': date.date(),
                    'time': f"{morning_hour:02d}:00",
                    'medication': med['name'],
                    'status': status,
                    'hour': morning_hour
                })
        
        st.session_state.doses_log = sample_data
    
    # Convert data for analysis
    df_doses = pd.DataFrame(st.session_state.doses_log)
    
    if not df_doses.empty:
        # Convert date to datetime if it's not already
        if 'date' in df_doses.columns:
            df_doses['date'] = pd.to_datetime(df_doses['date'])
            df_filtered = df_doses[df_doses['date'].dt.date > date_filter]
            
            # Ensure hour column exists
            if 'hour' not in df_filtered.columns and 'time' in df_filtered.columns:
                df_filtered['hour'] = df_filtered['time'].str.split(':').str[0].astype(int)
            
            # Analytics Sections
            tab1, tab2 = st.tabs(["Adherence Analytics", "Medication Insights"])
            
            with tab1:
                if not df_filtered.empty:
                    # Adherence Trend
                    st.markdown("### 📈 Adherence Trend")
                    daily_adherence = df_filtered.groupby(['date', 'status']).size().unstack(fill_value=0)
                    
                    if 'Taken' in daily_adherence.columns:
                        daily_adherence['adherence_rate'] = (daily_adherence['Taken'] / 
                            daily_adherence.sum(axis=1) * 100)
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=daily_adherence.index,
                            y=daily_adherence['adherence_rate'],
                            mode='lines+markers',
                            name='Adherence Rate',
                            line=dict(color='#2ecc71', width=2),
                            fill='tozeroy'
                        ))
                        fig.update_layout(
                            title='Daily Medication Adherence',
                            xaxis_title='Date',
                            yaxis_title='Adherence Rate (%)',
                            hovermode='x unified',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Time of Day Analysis
                    st.markdown("### ⏰ Time of Day Analysis")
                    if 'hour' in df_filtered.columns:
                        taken_doses = df_filtered[df_filtered['status'] == 'Taken']
                        if not taken_doses.empty:
                            hourly_doses = taken_doses.groupby('hour').size()
                            
                            fig_time = go.Figure(data=[
                                go.Bar(
                                    x=hourly_doses.index,
                                    y=hourly_doses.values,
                                    marker_color='#3498db'
                                )
                            ])
                            fig_time.update_layout(
                                title='Preferred Medication Times',
                                xaxis_title='Hour of Day',
                                yaxis_title='Number of Doses',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                            )
                            st.plotly_chart(fig_time, use_container_width=True)
                        else:
                            st.info("No taken doses recorded yet.")
                    else:
                        st.warning("Time information is not available for analysis.")
            
            with tab2:
                if not df_filtered.empty:
                    # Medication-specific insights
                    st.markdown("### 💊 Medication Insights")
                    
                    # Medication adherence comparison
                    med_adherence = df_filtered.groupby('medication')['status'].value_counts().unstack(fill_value=0)
                    if not med_adherence.empty:
                        med_adherence_pct = med_adherence.div(med_adherence.sum(axis=1), axis=0) * 100
                        
                        fig_med = go.Figure()
                        for status in ['Taken', 'Delayed', 'Missed']:
                            if status in med_adherence_pct.columns:
                                fig_med.add_trace(go.Bar(
                                    name=status,
                                    x=med_adherence_pct.index,
                                    y=med_adherence_pct[status],
                                    marker_color='#2ecc71' if status == 'Taken' 
                                               else '#f1c40f' if status == 'Delayed' 
                                               else '#e74c3c'
                                ))
                        
                        fig_med.update_layout(
                            barmode='stack',
                            title='Medication-wise Adherence',
                            yaxis_title='Percentage',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                        )
                        st.plotly_chart(fig_med, use_container_width=True)
                    else:
                        st.info("No medication adherence data available yet.")
        else:
            st.warning("Data format is incorrect. Please ensure medication logs contain date information.")
    else:
        st.info("No medication data available for analysis. Start logging your doses to see insights!")

elif selected == "Personal Info":
    st.title("👤 Personal Information")
    
    with st.form("personal_info_form"):
        st.session_state.personal_info['name'] = st.text_input("Full Name", 
            st.session_state.personal_info.get('name', ''))
        st.session_state.personal_info['age'] = st.number_input("Age", 
            value=int(st.session_state.personal_info.get('age', 0)) if st.session_state.personal_info.get('age') else 0)
        st.session_state.personal_info['address'] = st.text_area("Address", 
            st.session_state.personal_info.get('address', ''))
        st.session_state.personal_info['emergency_contact'] = st.text_input("Emergency Contact", 
            st.session_state.personal_info.get('emergency_contact', ''))
        
        if st.form_submit_button("Save Information"):
            st.success("Personal information updated successfully!")

elif selected == "Medications":
    st.title("💊 Medications Management")
    
    # Add new medication
    with st.expander("Add New Medication"):
        with st.form("add_medication"):
            med_name = st.text_input("Medication Name")
            dosage = st.text_input("Dosage")
            frequency = st.selectbox("Frequency", 
                ["Once daily", "Twice daily", "Three times daily", "As needed"])
            instructions = st.text_area("Special Instructions")
            
            if st.form_submit_button("Add Medication"):
                if med_name and dosage:
                    st.session_state.medications.append({
                        'name': med_name,
                        'dosage': dosage,
                        'frequency': frequency,
                        'instructions': instructions,
                        'stock': 30,
                        'refill_threshold': 10,
                        'category': 'Other'
                    })
                    st.success(f"Added {med_name} to medications list!")
    
    # List current medications
    st.subheader("Current Medications")
    if st.session_state.medications:
        for idx, med in enumerate(st.session_state.medications):
            with st.expander(f"{med['name']} - {med['dosage']}"):
                st.write(f"Frequency: {med['frequency']}")
                st.write(f"Instructions: {med['instructions']}")
                if st.button(f"Remove {med['name']}", key=f"remove_{idx}"):
                    st.session_state.medications.pop(idx)
                    st.rerun()
    else:
        st.write("No medications added yet")

    # Log a dose
    st.subheader("Log a Dose")
    with st.form("log_dose"):
        med_choice = st.selectbox("Select Medication", 
            [med['name'] for med in st.session_state.medications] if st.session_state.medications else ['No medications'])
        status = st.selectbox("Status", ["Taken", "Missed", "Delayed"])
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Log Dose"):
            if med_choice != 'No medications':
                st.session_state.doses_log.append({
                    'medication': med_choice,
                    'date': datetime.now().date().isoformat(),
                    'status': status,
                    'notes': notes
                })
                st.success("Dose logged successfully!")

elif selected == "Schedule":
    st.title("📅 Schedule and Reminders")
    
    # Add new reminder
    with st.expander("Add New Reminder"):
        with st.form("add_reminder"):
            med_choice = st.selectbox("Select Medication", 
                [med['name'] for med in st.session_state.medications] if st.session_state.medications else ['No medications'])
            reminder_date = st.date_input("Date")
            reminder_time = st.time_input("Time")
            reminder_note = st.text_area("Note")
            
            if st.form_submit_button("Set Reminder"):
                if med_choice != 'No medications':
                    reminder_datetime = datetime.combine(reminder_date, reminder_time)
                    st.session_state.reminders.append({
                        'medication': med_choice,
                        'datetime': reminder_datetime.isoformat(),
                        'note': reminder_note
                    })
                    st.success("Reminder set successfully!")

    # Calendar view
    st.subheader("Calendar")
    calendar_events = []
    for reminder in st.session_state.reminders:
        calendar_events.append({
            'title': f"{reminder['medication']}",
            'start': reminder['datetime'],
            'end': (datetime.fromisoformat(reminder['datetime']) + timedelta(minutes=30)).isoformat()
        })
    
    calendar(events=calendar_events)

elif selected == "Drone Service":
    st.title("🚁 Medication Delivery Drone")
    
    # Current Status Section with better styling
    st.markdown("""
        <div class='status-container'>
            <div class='status-card'>
                <h3>🛸 Drone Status</h3>
                <p class='status-text'>Available</p>
            </div>
            <div class='status-card'>
                <h3>📍 Current Location</h3>
                <p class='status-text'>Kitchen</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # House Layout Section
    st.markdown("### 🏠 House Layout")
    
    # Create a detailed house layout with multiple rooms and levels
    st.markdown("""
        <div class='house-container'>
            <!-- Second Floor -->
            <div class='floor second-floor'>
                <h4>Second Floor</h4>
                <div class='floor-layout'>
                    <div class='room master-bedroom'>
                        <h5>Master Bedroom</h5>
                        <span class='room-icon'>🛏️</span>
                    </div>
                    <div class='room bedroom-2'>
                        <h5>Bedroom 2</h5>
                        <span class='room-icon'>🛏️</span>
                    </div>
                    <div class='room bedroom-3'>
                        <h5>Bedroom 3</h5>
                        <span class='room-icon'>🛏️</span>
                    </div>
                    <div class='room bathroom-2'>
                        <h5>Bathroom</h5>
                        <span class='room-icon'>🚽</span>
                    </div>
                </div>
            </div>
            
            <!-- First Floor -->
            <div class='floor first-floor'>
                <h4>First Floor</h4>
                <div class='floor-layout'>
                    <div class='room living-room'>
                        <h5>Living Room</h5>
                        <span class='room-icon'>🛋️</span>
                    </div>
                    <div class='room kitchen'>
                        <h5>Kitchen</h5>
                        <span class='room-icon'>🍳</span>
                        <div class='drone' id='drone'>🚁</div>
                    </div>
                    <div class='room dining-room'>
                        <h5>Dining Room</h5>
                        <span class='room-icon'>🍽️</span>
                    </div>
                    <div class='room bathroom-1'>
                        <h5>Bathroom</h5>
                        <span class='room-icon'>🚽</span>
                    </div>
                </div>
            </div>
            
            <!-- Stairs -->
            <div class='stairs'>
                <span class='stairs-icon'>↗️</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Drone Controls
    st.markdown("### 🎮 Drone Controls")
    
    # Create columns for destination selection and actions
    col1, col2 = st.columns(2)
    
    with col1:
        destination = st.selectbox(
            "Select Destination",
            ["Master Bedroom", "Bedroom 2", "Bedroom 3", "Living Room", "Kitchen", "Dining Room"]
        )
    
    with col2:
        delivery_type = st.selectbox(
            "Delivery Type",
            ["Regular Delivery", "Express Delivery", "Scheduled Delivery"]
        )
    
    # Additional options
    st.markdown("#### Advanced Settings")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.checkbox("Avoid Stairs", value=True, help="Route drone to avoid stairs when possible")
    with col4:
        st.checkbox("Silent Mode", help="Reduce drone noise during delivery")
    with col5:
        st.checkbox("Return to Base", value=True, help="Return to kitchen after delivery")
    
    # Start Delivery Button
    if st.button("Start Delivery", key="start_delivery", help="Click to start drone delivery"):
        with st.spinner("🚁 Initializing drone delivery..."):
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.02)
            st.success(f"✅ Delivery completed! Medications have been delivered to {destination}.")
            
            if st.session_state.get("return_to_base", True):
                with st.spinner("🔄 Returning to kitchen..."):
                    time.sleep(1)
                    st.info("🏠 Drone has returned to base.")
