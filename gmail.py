'''This file does the following:
    --Read all Gmails in the inbox which are label as unread
    --Save its data (such as subject,sender,message) in a table(mails) of a database(email_record)
'''
from __future__ import print_function
import os.path
import mysql.connector
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)   
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Connect to the Gmail API
    
    service = build('gmail', 'v1', credentials=creds)
  
    # request a list of all the messages
    result = service.users().messages().list(userId='me', labelIds=['UNREAD'] ).execute()
  
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
    if not messages :
        print('NO unread messages')
  
    # messages is a list of dictionaries where each dictionary contains a message id.
    else:
    # iterate through all the messages
        for msg in messages:
            # Get the message from its id
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
    
            # Use try-except to avoid any Errors
            #try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt['payload']
            headers = payload['headers']

            # Look for Subject and Sender Email in the headers
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']

            # Printing the subject, sender's email and message
            print("Subject: ", subject)
            print("From: ", sender)
            print("Message: ", txt['snippet'])
            print('\n')
            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password"
            )
            cursor = conn.cursor()

            # Create a database
            cursor.execute("CREATE DATABASE IF NOT EXISTS email_record")
            cursor.execute("USE email_record")

            # Create a table
            table_create_query = '''CREATE TABLE IF NOT EXISTS mails (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender VARCHAR(255),
                subject VARCHAR(255),
                body TEXT
            )'''
            cursor.execute(table_create_query)

            # Insert data into the table
            insert_query = "INSERT INTO mails (sender, subject, body) VALUES (%s, %s, %s)"
            data = (sender,subject,txt['snippet'])
            cursor.execute(insert_query, data)

            # Commit the changes to the database
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            #except:
                #print("nothing")

if __name__ == '__main__':
    main()       
