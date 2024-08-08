import os
import datatime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google():
	creds = None
	# The file token.picle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
	if os.path.exists('token.picke'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)

	
	# if there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials/credentials.json', SCOPES
			)
			creds = flow.run_local_server(port=0)
		#save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	return build('calendar', 'v3', credentials=creds)

# list events
def list_events(service):
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	print('Getting the upcoming 10 events')
	events_result = service.events().list(calendarId='primary', timeMin=now,
									   maxResults=10, singleEvents=True,
									   orderBy='startTime').execute()
	
	events = events_result.get('items',[])

	if not events:
		print('No upcoming events found.')

	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		print(start, event['summary'])


#create event
def create_event(service):
	event = {
		'summary': 'Test Event',
		'location': '123 Main St, Anytown, USA',
		'description': 'A chance to test the Google Calendar API',
		'start': {
			 'dateTime': '2024-08-09T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2024-08-09T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [
            {'email': 'example@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },

	}		
	event = service.events().insert(calendarId='primary', body=event).execute()
	print('Event created: %s' % (event.get('htmlLink')))


#update event
def update_event(service, event_id):
	event = service.events().get(calendarId='primary', eventId=event_id).execute()
	event['summary'] = 'Upload Test Event'
	updated_event = service.events().update(calendarId='primary',eventId=event['Id'], body = event).execute()
	print('Event updated: %s' %(updated_event.get('htmlLink')))


#delete events
def delete_event(service, event_id):
	service.events().delete(calendarId='primary', eventId = event_id).execute()
	print('Event deleted.')

import argparse

def main():
	service = authenticate_google()
	parser = argparse.ArgumentParser(description='Google Calendar Automation')
	parser.add_argument('command', choices=['list', 'create', 'update', 'delete'], help='Command to execute')
	parser.add_argument('--event_id', help = 'Event ID (for update and delete commands)')
	args = parser.parse_args()


	if args.command == 'list':
		list_events(service)
	elif args.command == 'create':
		create_event(service)
	elif args.command == 'update':
		if args.event_id:
			update_event(service, args.event_id)
		else:
			print('Event ID is required for update.')
	elif args.command == 'delete':
		if args.event_id:
			delete_event(service, args.event_id)
		else:
			print('Event ID is required for deletion.')

if __name__ == '__main__':
	main()
