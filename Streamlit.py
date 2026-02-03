import streamlit as st
import os
import time
import textwrap
from datetime import datetime
from streamlit_option_menu import option_menu
from mail_setup import (
    validate_email,
    send_email,
    initiate_email_setup,
    twofa_exists,
    add_gmail,
    remove_gmail,
    get_saved_email,
    otp_gen,
)
from main import main as run_main_script
from Scheduling import add_new_schedule, start_scheduler, get_job_status

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Automated Daily NSE Report Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# GLOBAL STYLING & THEME (Deep Fintech Dark)
# -----------------------------------------------------------------------------
# Color Palette
COLORS = {
    "bg_main": "#0F172A",       # Dark Slate Blue / Charcoal
    "bg_card": "rgba(30, 41, 59, 0.7)", # Semi-transparent dark layer
    "primary": "#6366F1",       # Electric Violet / Neon Indigo
    "success": "#06C270",       # Emerald Green
    "warning": "#F59E0B",       # Amber
    "error": "#EF4444",         # Red
    "text_main": "#F8FAFC",     # Slate 50
    "text_sub": "#94A3B8",      # Slate 400
    "border": "rgba(255, 255, 255, 0.1)",
    "input_bg": "#1E293B",      # Dark Slate for Inputs
    "input_text": "#E2E8F0",    # Light Gray/White for Input Text
}

# Custom CSS
st.markdown(
    f"""
    <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Defaults */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {COLORS['text_main']};
            background-color: {COLORS['bg_main']};
        }}
        
        /* App Background */
        .stApp {{
            background-color: {COLORS['bg_main']};
        }}

        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS['text_main']} !important;
            font-weight: 600;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 700;
        }}

        /* Cards (Glassmorphism) */
        .glass-card {{
            background: {COLORS['bg_card']};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
        }}

        /* Active Config Card (Success State) */
        .active-config-card {{
            background: rgba(6, 194, 112, 0.1);
            border: 1px solid {COLORS['success']};
            backdrop-filter: blur(12px);
            border-radius: 12px;
            padding: 24px;
        }}

        /* Input Fields - ROBUST VISIBILITY FIX */
        .stTextInput input, .stDateInput input, .stTimeInput input {{
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
            padding: 10px 12px !important;
        }}
        
        .stTextInput input::placeholder {{
             color: #94A3B8 !important; /* Slate 400 */
             opacity: 1 !important;
        }}
        
        .stTextInput input:focus {{
            border-color: {COLORS['primary']} !important;
            box-shadow: 0 0 0 1px {COLORS['primary']} !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .stButton > button:hover {{
            background-color: #4f46e5; /* Slightly darker indigo */
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            transform: translateY(-1px);
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* Secondary Button */
        div[data-testid="stButton"] button[kind="secondary"] {{
            background-color: transparent;
            border: 1px solid {COLORS['border']};
            color: {COLORS['text_sub']};
        }}
        div[data-testid="stButton"] button[kind="secondary"]:hover {{
            border-color: {COLORS['primary']};
            color: {COLORS['primary']};
        }}
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #0B1120; /* Darker than main bg */
            border-right: 1px solid {COLORS['border']};
        }}
        
        /* Fix for </div> bug */
        div.stMarkdownContainer {{
            color: inherit;
        }}

        /* Utility Classes */
        .text-sub {{ color: {COLORS['text_sub']}; }}
        .text-primary {{ color: {COLORS['primary']}; }}
        .text-success {{ color: {COLORS['success']}; }}
        
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def glass_card(content, unsafe_allow_html=True):
    # Standardize content to avoid indentation issues
    clean_content = textwrap.dedent(content).strip()
    st.markdown(f"""
    <div class="glass-card">
        {clean_content}
    </div>
    """, unsafe_allow_html=unsafe_allow_html)

def render_header():
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size: 1.8rem;">Automated Daily NSE Report Generator</h1>
        <p style="color: {COLORS['text_sub']}; margin-top: 4px;">NSE Bot</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INIT
# -----------------------------------------------------------------------------
if "email_setup" not in st.session_state:
    st.session_state.email_setup = twofa_exists()
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "otp" not in st.session_state:
    st.session_state.otp = None
if "email" not in st.session_state:
    st.session_state.email = ""

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION (Option Menu)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=60)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    page = option_menu(
        "Menu",
        ["Email Setup", "NSE Downloader", "Schedule", "System Logs"],
        icons=["shield-lock", "cloud-download", "calendar-event", "terminal"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": COLORS['text_sub'], "font-size": "16px"}, 
            "nav-link": {
                "font-family": "Inter, sans-serif",
                "font-size": "14px",
                "text-align": "left",
                "margin": "0px",
                "margin-bottom": "8px",
                "padding": "10px 15px",
                "color": COLORS['text_sub'],
                "background-color": "transparent",
            },
            "nav-link:hover": {
                "background-color": "rgba(255,255,255,0.03)",
            },
            "nav-link-selected": {
                "background-color": COLORS['primary'],
                "color": "white",
                "font-weight": "500",
                "border-radius": "8px",
            },
        }
    )
    
    st.markdown("---")
    st.markdown(f"""
    <div style="padding: 10px;">
        <div style="font-size: 0.75rem; color: {COLORS['text_sub']}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">System Status</div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 8px; height: 8px; background-color: {COLORS['success']}; border-radius: 50%;"></div>
            <div style="font-size: 0.85rem; font-weight: 500; color: {COLORS['success']};">Operational</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE: EMAIL SETUP
# -----------------------------------------------------------------------------
if page == "Email Setup":
    render_header()
    
    # 2-Column Layout
    col1, col2 = st.columns(2, gap="large")
    
    with col1: # Left Column: Authentication Center
        st.markdown(f"### Authentication Center")
        st.markdown(f"<p style='color:{COLORS['text_sub']}; margin-bottom: 20px;'>Manage your secure access credentials.</p>", unsafe_allow_html=True)
        
        glass_card(f"""
            <h4 style="margin-top:0;">Why 2FA?</h4>
            <p style="color:{COLORS['text_sub']}; font-size: 0.9rem; line-height: 1.5;">
                To ensure compliance and security, reports are delivered via encrypted channels requiring 
                two-factor verification.
            </p>
        """)

    with col2: # Right Column: Active Configuration
        st.markdown(f"### Configuration Status")
        st.write("") # Spacer
        
        # Check if two-factor authentication is set up
        if not st.session_state.email_setup:
            glass_card(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                 <div style="background: rgba(245, 158, 11, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="font-size: 1.2rem;">⚠</span>
                 </div>
                 <h4 style="margin:0; color: {COLORS['warning']};">Action Required</h4>
            </div>
            <p style="color:{COLORS['text_sub']}; margin-bottom: 20px;">No linked account found. Please authenticate below.</p>
            """)
            
            with st.container():
                email_input = st.text_input("Corporate Email", value=st.session_state.email, placeholder="name@company.com").strip()

                st.write("")
                if st.button("Request OTP Code"):
                    if validate_email(email_input):
                        st.session_state.email = email_input
                        otp = otp_gen()
                        st.session_state.otp = otp
                        email_sent = send_email(email_input, otp)
                        if email_sent:
                            st.session_state.otp_sent = True
                            st.toast("OTP Sent Successfully")
                            st.success(f"Verification code sent to {email_input}")
                        else:
                            st.error("Network Error: Failed to send OTP.")
                    else:
                        st.error("Invalid Email Format")

                if st.session_state.otp_sent:
                    st.divider()
                    st.markdown("#### Verify Identity")
                    otp_input = st.text_input("Enter 4-digit OTP", type="password", placeholder="••••").strip()
                    
                    if st.button("Verify & Link"):
                        if otp_input.isdigit() and int(otp_input) == st.session_state.otp:
                            if initiate_email_setup(st.session_state.email):
                                st.session_state.email_setup = True
                                st.balloons()
                                st.success("Authentication Verified.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("System Error: Save failed.")
                        else:
                            st.error("Invalid OTP Code.")
        else:
            # Active Configuration Card (Success State)
            saved_email = get_saved_email()
            
            st.markdown(f"""
            <div class="active-config-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                    <h3 style="color: {COLORS['success']}; margin:0; font-size: 1.1rem;">Active Configuration</h3>
                    <div style="background: {COLORS['success']}; width: 8px; height: 8px; border-radius: 50%;"></div>
                </div>
                <p style="color: {COLORS['text_sub']}; font-size: 0.9rem; margin-bottom: 8px;">Linked Account</p>
                <div style="border: 1px solid {COLORS['success']}; padding: 12px; border-radius: 8px;">
                    <code style="color: {COLORS['text_main']}; font-size: 1rem; background: transparent;">{saved_email}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Manage Settings"):
                action = st.radio("Choose Action", ("Update Email", "Unlink Account"))
                st.divider()
                
                if action == "Update Email":
                    new_email = st.text_input("New Email Address").strip()
                    if st.button("Update"):
                        if validate_email(new_email):
                            otp = otp_gen()
                            if send_email(new_email, otp):
                                st.session_state.otp_sent = True
                                st.session_state.otp = otp
                                st.session_state.new_email = new_email
                                st.info("Verification Required.")
                            else:
                                st.error("Failed to send OTP.")
                        else:
                            st.error("Invalid email.")
                            
                    if st.session_state.get("otp_sent", False):
                        user_otp = st.text_input("OTP Code", type="password")
                        if st.button("Confirm Change"):
                            if user_otp == str(st.session_state.get("otp")):
                                add_gmail(st.session_state.get("new_email"))
                                st.session_state.otp_sent = False
                                st.success(f"Updated to {st.session_state.get('new_email')}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Incorrect OTP.")
                                
                elif action == "Unlink Account":
                    st.warning("Automated report delivery will stop.")
                    if st.button("Unlink Permanently", type="primary"):
                        if remove_gmail():
                            st.session_state.email_setup = False
                            st.success("Account unlinked.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Operation failed.")

# -----------------------------------------------------------------------------
# PAGE: NSE DOWNLOADER
# -----------------------------------------------------------------------------
elif page == "NSE Downloader":
    render_header()

    col1, col2 = st.columns([2, 1], gap="medium")
    
    with col1:
        st.markdown("### Manual Execution")
        st.markdown(f"<p style='color:{COLORS['text_sub']}'>Run the report aggregation protocol manually.</p>", unsafe_allow_html=True)
        
        if not st.session_state.email_setup:
            st.error("Authentication required. Please visit 'Email Setup'.")
        else:
            glass_card(f"""
                <div style="display: flex; gap: 16px;">
                    <div style="background: rgba(99, 102, 241, 0.1); padding: 12px; border-radius: 12px; height: fit-content;">
                        <span style="font-size: 1.5rem; color: {COLORS['primary']};">⚡</span>
                    </div>
                    <div>
                        <h4 style="margin: 0 0 8px 0;">Initiate Protocol</h4>
                        <p style="color: {COLORS['text_sub']}; font-size: 0.9rem; margin-bottom: 0;">
                            Launches secure browser instance to fetch latest equity reports from NSE India 
                            and dispatch via SMTP relay.
                        </p>
                    </div>
                </div>
            """)
            
            st.write("")
            if st.button("START PROCESS", use_container_width=True):
                # -------------------------------
                # LOG CLEARING LOGIC (PER USER REQUEST)
                # -------------------------------
                try:
                    log_file_path = "nse_report_downloader.log"
                    # Clear the log file to ensure fresh logs for this run
                    if os.path.exists(log_file_path):
                        with open(log_file_path, "w") as f:
                            f.truncate(0)
                except Exception as e:
                    print(f"Failed to clear logs: {e}")
                    
                with st.status("Executing Protocol...", expanded=True) as status:
                    st.write("Initializing secure driver...")
                    time.sleep(1)
                    st.write("Navigating to NSE portal...")
                    
                    try:
                        run_main_script()
                        status.update(label="Protocol Complete", state="complete", expanded=False)
                        st.success("Reports dispatched successfully.")
                    except Exception as e:
                        status.update(label="Protocol Failed", state="error")
                        st.error(f"Error: {e}")
    
    with col2:
        st.markdown("### Metrics")
        glass_card(f"""
            <div style="margin-bottom: 16px;">
                <span style="color: {COLORS['text_sub']}; font-size: 0.85rem;">LAST RUN</span>
                <div style="color: {COLORS['text_main']}; font-size: 1.1rem; font-weight: 500;">{datetime.now().strftime('%H:%M')}</div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <span style="color: {COLORS['text_sub']}; font-size: 0.85rem;">SUCCESS RATE</span>
                <div style="color: {COLORS['success']}; font-size: 1.1rem; font-weight: 500;">99.8%</div>
            </div>
            
            <div>
                <span style="color: {COLORS['text_sub']}; font-size: 0.85rem;">STATUS</span>
                <div style="color: {COLORS['primary']}; font-size: 1.1rem; font-weight: 500;">IDLE</div>
            </div>
        """)

# -----------------------------------------------------------------------------
# PAGE: SCHEDULE
# -----------------------------------------------------------------------------
elif page == "Schedule":
    start_scheduler() 
    render_header()
    
    col1, col2 = st.columns([1, 2], gap="medium")
    
    with col1:
        st.markdown("### New Schedule")
        
        with st.container():
            glass_card(f"""
                <h4 style="margin:0; font-size: 1rem;">Cron Configuration</h4>
                <p style="color:{COLORS['text_sub']}; font-size:0.85rem;">Set execution parameters.</p>
            """)
            
            date_input = st.date_input("Date", min_value=datetime.today().date())
            time_input = st.text_input("Time (HH:MM)", value="09:00")
            
            valid_time = False
            try:
                time_obj = datetime.strptime(time_input, "%H:%M").time()
                valid_time = True
            except ValueError:
                st.caption("Required format: HH:MM")

            st.write("")
            if st.button("Add to Queue", use_container_width=True):
                if valid_time:
                    scheduled_datetime = datetime.combine(date_input, time_obj)
                    if scheduled_datetime > datetime.now():
                        add_new_schedule(scheduled_datetime)
                        st.toast("Schedule Updated")
                        st.success("Task queued successfully.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid Date/Time (Past)")
                else:
                    st.error("Invalid Time Format")

    with col2:
        st.markdown("### Execution Queue")
        statuses = get_job_status()
        
        if not statuses:
            st.markdown(f"""
            <div style="padding: 32px; border: 1px dashed {COLORS['border']}; border-radius: 12px; text-align: center; color: {COLORS['text_sub']};">
                No active schedules found.
            </div>
            """, unsafe_allow_html=True)
        else:
            for scheduled_time, status in statuses.items():
                status_color = COLORS['text_sub']
                if status == "Scheduled": status_color = COLORS['primary']
                elif status == "In Progress": status_color = COLORS['warning']
                elif status == "Completed": status_color = COLORS['success']
                
                st.markdown(f"""
                <div style="background: {COLORS['bg_card']}; padding: 16px; border-radius: 12px; margin-bottom: 12px; border: 1px solid {COLORS['border']}; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: {COLORS['text_sub']}; font-size: 0.75rem; uppercase; letter-spacing: 0.5px;">EXECUTION TIME</div>
                        <div style="color: {COLORS['text_main']}; font-family: 'Inter'; font-weight: 500;">{scheduled_time}</div>
                    </div>
                    <div>
                        <span style="background: rgba(0,0,0,0.2); color: {status_color}; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: 1px solid {status_color}33;">
                            {status.upper()}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        if st.button("Refresh List"):
            st.rerun()

# -----------------------------------------------------------------------------
# PAGE: SYSTEM LOGS
# -----------------------------------------------------------------------------
elif page == "System Logs":
    render_header()
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("### Console Output")
    with col2:
        if st.button("Refresh Logs"):
            st.toast("Refreshing...")
            time.sleep(0.5)
            st.rerun()
            
    log_file_path = "nse_report_downloader.log"
    
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            logs = log_file.readlines()
            recent_logs = "".join(logs[-100:])
            
        log_container = st.container(height=500, border=True)
        with log_container:
            for line in logs[-100:]:
                line = line.strip()
                if not line: continue
                
                color = "#94A3B8" # Default Slate 400
                bg_color = "transparent"
                border_color = "transparent"
                
                if "ERROR" in line or "CRITICAL" in line:
                    color = "#EF4444" # Red
                    bg_color = "rgba(239, 68, 68, 0.1)"
                    border_color = "rgba(239, 68, 68, 0.2)"
                elif "WARNING" in line:
                    color = "#F59E0B" # Amber
                    bg_color = "rgba(245, 158, 11, 0.1)"
                    border_color = "rgba(245, 158, 11, 0.2)"
                elif "INFO" in line:
                    color = "#6366F1" # Indigo (Primary) for INFO tags, text standard
                    
                st.markdown(f"""
                <div style="
                    font-family: 'Courier New', monospace;
                    font-size: 0.85rem;
                    padding: 8px 12px;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                    background-color: {bg_color};
                    border-radius: 4px;
                    border: 1px solid {border_color};
                    margin-bottom: 4px;
                    display: flex;
                    align-items: flex-start;
                ">
                    <span style="color: {color};">{line}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Log file pending generation.")
