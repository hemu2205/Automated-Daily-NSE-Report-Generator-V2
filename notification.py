import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

# Function to get the receiver's email from the configuration file
def get_receiver_add():
    try:
        with open("config.txt") as f:
            email = f.read().strip()  
            if email:
                return email
    except FileNotFoundError:
        logging.error("Config file not found. Initiating email setup.")
        return None

# Define the log file path as a constant
LOG_FILE_PATH = "nse_report_downloader.log"

# Function to send the email with the provided details
def send_mail(status, num_downloaded, num_validated, num_renamed):
    # Set up the email parameters
    message = MIMEMultipart()
    message["From"] = 'nsebot22@gmail.com'
    password = "lzbq ocrr lqpr ilxg"
    receiver_add = get_receiver_add()
    message["Subject"] = "NSE BOT REPORT RETRIEVAL AUTOMATION RUN DETAILS"
    
    # Check if the receiver email is available
    if not receiver_add:
        logging.error("Receiver email address is not specified.")
        # raise ValueError("Receiver email address is not specified.") 
        return # Don't raise, just log
    
    message["To"] = receiver_add

    # Compose the body of the email with dynamic content
    body = f"""
    Hello,

    This is the summary of the latest report download automation run.

    Overall Status: {status}
    
    Number of Files that Downloaded: {num_downloaded}
    Number of Files that are Validated: {num_validated}
    Number of Files Renamed: {num_renamed}

    Regards,
    NSE Report Automation
    """

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    # Attach the log file to the email
    log_file = LOG_FILE_PATH
    try:
        if os.path.exists(log_file):
            with open(log_file, "rb") as attachment:
                mime_base = MIMEBase("application", "octet-stream")
                mime_base.set_payload(attachment.read())
                encoders.encode_base64(mime_base)
                mime_base.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(log_file)}"
                )
                message.attach(mime_base)
        else:
             logging.warning(f"Log file not found at: {log_file}")
    except Exception as e:
        logging.error(f"Error attaching log file: {e}")

    # Send the email
    try:
        logging.info(f"Attempting to send email to {receiver_add}...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(message["From"], password)
            server.send_message(message)
            logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Error occurred while sending email: {e}")