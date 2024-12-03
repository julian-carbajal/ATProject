import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from streamlit_option_menu import option_menu
from streamlit_calendar import calendar
import random
import seaborn as sns
import numpy as np
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts
import hydralit_components as hc
from streamlit_card import card

# Set page config
st.set_page_config(
    page_title="MedTracker Pro",
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

if 'notifications' not in st.session_state:
    st.session_state.notifications = [
        {'type': 'warning', 'message': 'Aspirin supply running low. Consider refill.'},
        {'type': 'info', 'message': 'New feature: Medication interaction checker now available!'},
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
    
    # Time period selector with modern tabs
    time_options = [
        {'label': "Last 7 Days", 'icon': "calendar"},
        {'label': "Last 30 Days", 'icon': "calendar"},
        {'label': "Last 6 Months", 'icon': "calendar"}
    ]
    
    time_period = hc.option_bar(
        option_definition=time_options,
        title='Select Time Period',
        key='time_period',
        override_theme={'txc_inactive': '#777'},
        horizontal_orientation=True
    )
    
    if time_period == "Last 7 Days":
        date_filter = datetime.now().date() - timedelta(days=7)
    elif time_period == "Last 30 Days":
        date_filter = datetime.now().date() - timedelta(days=30)
    else:
        date_filter = datetime.now().date() - timedelta(days=180)
    
    # Convert data for analysis
    df_doses = pd.DataFrame(st.session_state.doses_log)
    df_doses['date'] = pd.to_datetime(df_doses['date'])
    df_filtered = df_doses[df_doses['date'].dt.date > date_filter]
    
    # Advanced Analytics Sections
    tab1, tab2, tab3 = st.tabs(["Adherence Analytics", "Time Patterns", "Medication Insights"])
    
    with tab1:
        # Adherence Trend
        st.markdown("### 📈 Adherence Trend")
        daily_adherence = df_filtered.groupby(['date', 'status']).size().unstack(fill_value=0)
        daily_adherence['adherence_rate'] = daily_adherence['Taken'] / daily_adherence.sum(axis=1) * 100
        
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
    
    with tab2:
        # Time Pattern Analysis
        st.markdown("### 🕒 Time Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap of medication times
            df_filtered['hour'] = df_filtered['date'].dt.hour
            df_filtered['day'] = df_filtered['date'].dt.day_name()
            
            pivot_data = df_filtered.pivot_table(
                values='status',
                index='day',
                columns='hour',
                aggfunc='count',
                fill_value=0
            )
            
            fig_heatmap = px.imshow(
                pivot_data,
                color_continuous_scale='Viridis',
                title='Medication Time Patterns',
                labels={'x': 'Hour of Day', 'y': 'Day of Week', 'color': 'Doses'}
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Radar chart of daily patterns
            daily_counts = df_filtered.groupby('day').size()
            
            radar_data = {
                'title': {
                    'text': 'Daily Medication Pattern'
                },
                'radar': {
                    'indicator': [{'name': day, 'max': daily_counts.max()} for day in daily_counts.index]
                },
                'series': [{
                    'type': 'radar',
                    'data': [{'value': daily_counts.values.tolist()}],
                    'areaStyle': {'opacity': 0.3}
                }]
            }
            st_echarts(options=radar_data, height="400px")
    
    with tab3:
        # Medication-specific insights
        st.markdown("### 💊 Medication Insights")
        
        # Medication adherence comparison
        med_adherence = df_filtered.groupby('medication')['status'].value_counts().unstack()
        med_adherence_pct = med_adherence.div(med_adherence.sum(axis=1), axis=0) * 100
        
        fig_med = go.Figure()
        for status in ['Taken', 'Delayed', 'Missed']:
            fig_med.add_trace(go.Bar(
                name=status,
                x=med_adherence_pct.index,
                y=med_adherence_pct[status],
                marker_color='#2ecc71' if status == 'Taken' else '#f1c40f' if status == 'Delayed' else '#e74c3c'
            ))
        
        fig_med.update_layout(
            barmode='stack',
            title='Medication-wise Adherence',
            yaxis_title='Percentage',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_med, use_container_width=True)

# Personal Information
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

# Medications Management
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

# Schedule and Calendar
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

# Drone Service
elif selected == "Drone Service":
    st.title("🚁 Drone Delivery Service")
    
    # House layout data
    walls = [
        # Outer walls
        dict(type='rect', x0=0, y0=0, x1=100, y1=80, line=dict(color='black', width=2), fillcolor='white'),
        # Living room
        dict(type='rect', x0=5, y0=5, x1=45, y1=40, line=dict(color='gray', width=1), fillcolor='rgba(200,200,200,0.1)'),
        # Kitchen
        dict(type='rect', x0=50, y0=5, x1=95, y1=40, line=dict(color='gray', width=1), fillcolor='rgba(200,200,200,0.1)'),
        # Bathroom
        dict(type='rect', x0=70, y0=45, x1=95, y1=75, line=dict(color='gray', width=1), fillcolor='rgba(173,216,230,0.2)'),
        # Bedroom
        dict(type='rect', x0=5, y0=45, x1=65, y1=75, line=dict(color='gray', width=1), fillcolor='rgba(200,200,200,0.1)'),
    ]

    # Room labels
    annotations = [
        dict(x=25, y=22.5, text='Living Room', showarrow=False),
        dict(x=72.5, y=22.5, text='Kitchen', showarrow=False),
        dict(x=82.5, y=60, text='Bathroom', showarrow=False),
        dict(x=35, y=60, text='Bedroom', showarrow=False),
    ]

    # Create the base layout
    fig = go.Figure()

    # Add walls and rooms
    for wall in walls:
        fig.add_shape(wall)

    # Add room labels
    for annotation in annotations:
        fig.add_annotation(annotation)

    # Drone path coordinates
    if st.session_state.drone_status == 'In Transit':
        # Entry point (kitchen window)
        entry_point = (95, 20)
        # Bathroom medicine cabinet
        target_point = (82, 60)
        
        # Calculate intermediate points for smooth path
        path_x = [entry_point[0]]
        path_y = [entry_point[1]]
        
        # Add points to create a curved path
        path_x.extend([90, 85, 82])
        path_y.extend([30, 45, 60])

        # Add drone path
        fig.add_trace(go.Scatter(
            x=path_x,
            y=path_y,
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name='Drone Path'
        ))

        # Add drone marker
        fig.add_trace(go.Scatter(
            x=[path_x[-1]],
            y=[path_y[-1]],
            mode='markers',
            marker=dict(symbol='hexagon', size=15, color='red'),
            name='Drone'
        ))

        # Add start and end markers
        fig.add_trace(go.Scatter(
            x=[entry_point[0]],
            y=[entry_point[1]],
            mode='markers+text',
            marker=dict(symbol='star', size=12, color='green'),
            text=['Entry'],
            textposition='top center',
            name='Entry Point'
        ))
        
        fig.add_trace(go.Scatter(
            x=[target_point[0]],
            y=[target_point[1]],
            mode='markers+text',
            marker=dict(symbol='star', size=12, color='blue'),
            text=['Target'],
            textposition='top center',
            name='Medicine Cabinet'
        ))

    # Update layout
    fig.update_layout(
        title='Home Layout & Drone Path',
        showlegend=True,
        width=800,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[-5, 105]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[-5, 85],
            scaleanchor='x',
            scaleratio=1
        )
    )

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Request Medication Pickup")
        with st.form("drone_request"):
            pickup_location = st.text_input("Pharmacy Address")
            delivery_location = st.text_input("Delivery Address", 
                st.session_state.personal_info.get('address', ''))
            medication_details = st.text_area("Medication Details")
            
            if st.form_submit_button("Request Drone"):
                if pickup_location and delivery_location:
                    st.session_state.drone_status = 'In Transit'
                    st.success("Drone dispatched! Estimated delivery time: 30 minutes")
                    st.rerun()
    
    with col2:
        st.subheader("Live Drone Tracking")
        st.plotly_chart(fig, use_container_width=True)
        
        if st.session_state.drone_status == 'In Transit':
            # Simulate drone progress
            progress = st.progress(0)
            status_text = st.empty()
            
            if st.button("Simulate Delivery"):
                for i in range(100):
                    progress.progress(i + 1)
                    if i < 33:
                        status_text.text("🚁 Drone en route to pharmacy...")
                    elif i < 66:
                        status_text.text("📦 Picking up medication...")
                    else:
                        status_text.text("🏠 Delivering to your location...")
                st.session_state.drone_status = 'Available'
                st.success("✅ Delivery completed!")
                st.rerun()
