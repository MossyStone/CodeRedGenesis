from flask import Flask, render_template, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import json
import base64
import requests

# Constructing the relative path to the templates folder
TEMPLATES_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, static_folder='templates\static')

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Set the file path to the credentials.json file
CREDENTIALS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'creds', 'credentials.json')

#start of py scripts
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

#old email vaildation switched over to javascript validation for email
"""def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)"""

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
#End of py scripts

#Start of API calls
    # Amadeus API request function
def amadeus_request(origin, destination, departure_date, return_date):
    token = 'VliefaCN6z0MeLlcg1VD2AGGGYr7'
    headers = {'Authorization': 'Bearer ' + token}
    url = f'https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={origin}&destinationLocationCode={destination}&departureDate={departure_date}&returnDate={return_date}&adults=1&nonStop=false&max=100'
    resp = requests.get(url, headers=headers)
    offers = resp.json()["data"]
    prices = [float(offer["price"]["grandTotal"]) for offer in offers]
    return prices
#end of API calls

#HTML INDEX PAGES
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # Extract form data
        origin = request.form['origin']
        destination = request.form['destination']
        departure_date = request.form['d-date']
        return_date = request.form['r-date']
        
        # Call the amadeus_request function with form data to fetch flight offer prices
        flight_prices = amadeus_request(origin, destination, departure_date, return_date)
        return render_template('index.html', flight_prices=flight_prices)
    else:
        return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/chat')
def chat():
    return render_template('about.html')

@app.route('/index', methods=['POST'])
def send_email_request():
    user_email = request.form['email']
    message = request.form['subject']

    # Validate email address
    if not is_valid_email(user_email):
        return 'Invalid email address'

    # Send message body to specified email address
    send_email(sender=user_email, recipient="nowmeetarrow909@gmail.com", subject="User Inquiry", body=f"User Email: {user_email}\n\n{message}")

    # Send confirmation email to user
    send_email(sender="nowmeetarrow909@gmail.com", recipient=user_email, subject="Your Request", body="Dear User,\n\nThank you for contacting us. We have received your request and will get back to you shortly.\n\nBest regards,\nThe Team")

    return render_template('index.html')

if __name__ == '__main__':
    port = get_port_from_credentials(CREDENTIALS_FILE_PATH)
    app.run(host='0.0.0.0', port=port, debug=True)