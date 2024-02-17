from flask import Flask, render_template, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import json
import base64
import re

app = Flask(__name__)

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Set the file path to the credentials.json file
CREDENTIALS_FILE_PATH = "C:/Users/Madison/Desktop/Data Struc/Code Red/credentials.json"

def get_port_from_credentials(credentials_file_path):
    """Extracts the port number from the redirect URI in the credentials JSON file."""
    with open(credentials_file_path, 'r') as f:
        credentials = json.load(f)
        web_credentials = credentials.get('web', {})
        redirect_uris = web_credentials.get('redirect_uris', [])
        if redirect_uris:
            redirect_uri = redirect_uris[0]  # Assuming the redirect URI is the first one in the list
            port = int(redirect_uri.split(':')[-1].rstrip('/'))
        else:
            # Default port if 'redirect_uris' is not present or empty
            port = 15200
    return port

def is_valid_email(email):
    """Check if the given string is a valid email address."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

def send_email(sender, recipient, subject, body):
    """Function to send email."""
    # Load previously stored credentials from token.pickle if available.
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE_PATH, SCOPES)
            port = get_port_from_credentials(CREDENTIALS_FILE_PATH)
            creds = flow.run_local_server(port=port)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Initialize Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Create email message
    message_content = f'From: {sender}\nTo: {recipient}\nSubject: {subject}\n\n{body}'
    
    # Encode message content in Base64
    encoded_message = base64.urlsafe_b64encode(message_content.encode()).decode()

    # Create raw email message
    raw_message = {'raw': encoded_message}

    try:
        # Send email
        message = service.users().messages().send(userId='me', body=raw_message).execute()
        return 'Email sent successfully'
    except Exception as e:
        print(e)
        return 'Error sending email: ' + str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sendEmail', methods=['POST'])
def send_email_request():
    user_email = request.form['email']
    message = request.form['message']

    # Validate email address
    if not is_valid_email(user_email):
        return 'Invalid email address'

    # Send message body to specified email address
    send_email(sender=user_email, recipient="nowmeetarrow909@gmail.com", subject="User Inquiry", body=f"User Email: {user_email}\n\n{message}")

    # Send confirmation email to user
    send_email(sender="nowmeetarrow909@gmail.com", recipient=user_email, subject="Your Request", body="Dear User,\n\nThank you for contacting us. We have received your request and will get back to you shortly.\n\nBest regards,\nThe Team")

    return 'Emails sent successfully'

@app.route('/results', methods=['POST'])
def display_results():
    if request.method == 'POST':
        submitted_text = request.form.get('text')
        return render_template('results.html', submitted_text=submitted_text)
    else:
        return "Method Not Allowed", 405
    
@app.route('/sendIt', methods=['POST'])
def sendItenary():
    if request.method == 'POST':
        send_email_flag = request.form.get('send_email')  # Check if user wants to receive email
        email = request.form.get('email')  # Get user's email address
        submitted_text = request.form.get('text')  # Get submitted text

        if send_email_flag and email:  # If user wants to receive email and provided an email address
            sender_email = 'your_email@gmail.com'  # Replace with your email
            subject = 'Your Itinerary'
            body = f'Here is your submitted text: {submitted_text}'  # Customize email body

            # Send email
            if send_email(sender_email, email, subject, body):
                return 'Email sent successfully'
            else:
                return 'Failed to send email. Please try again later.'

    return 'Invalid request'

if __name__ == '__main__':
    port = get_port_from_credentials(CREDENTIALS_FILE_PATH)
    app.run(host='0.0.0.0', port=port, debug=True)
