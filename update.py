from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

test_calendar = "c_a8250bb9bcb5c691746693d42541f09b7e5bdc1ee6eac7dad4fc8ffb02dde462@group.calendar.google.com"
cyclotron_facility_use = "rr683mb1llhgtj1lvpu1f10jro@group.calendar.google.com"
current_cal = test_calendar

def main(allEvents):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
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

    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        with open('eventIDs.txt','r+') as ids: 
            for id in ids:
                id = id.rstrip()
                if service.events().get(calendarId=current_cal, eventId=id).execute():
                    event = service.events().get(calendarId=current_cal, eventId=id).execute()
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    if start > now:
                        service.events().delete(calendarId=current_cal, eventId=event["id"]).execute()
            ids.truncate(0)
            ids.close()
        print(allEvents)
        with open('eventIDs.txt', 'w') as f:
            for index in allEvents.index:
                created_event = service.events().quickAdd(
                calendarId=current_cal,
                text = allEvents["Type"][index] + " on " + allEvents["Time"][index]).execute()
                f.write(created_event["id"] + "\n")
        f.close()

    except HttpError as error:
        print('An error occurred: %s' % error)

#allEvents = dataframe consisting of all events to be added to calendar

def grabEvents():
    #name of file to be read
    filename = "CyclotronSched.html"

    #use BeautifulSoup package to put parser onto file
    with open(filename) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    #find all span elements to create array of text in file
    data = np.array(soup.find_all("span"))

    #iterate through array, stripping whitespace from each value
    for index, value in enumerate(data):
        data[index] = np.char.strip(value)
        
        #test
    data_length = data.size

    #remove header text and column indices
    data = data[8::] 

    #resize the data into rows and columns
    data = np.reshape(data, ((int((data_length-8)/6)),6))

    #create a dataframe using data with appropriate column headers
    df = pd.DataFrame(data, columns=["ID", "Time", "Desc.", "Location", "MD", "Notes"])

    #remove rows with lunch and repeated column headers
    df = df[df["ID"] != "null"]
    df = df[df["ID"] != "App_DtTm"]

    #drop the ID column to protect patient info
    df = df.drop(["ID"], axis =1)

    #drop unnecessary columns
    df = df.drop(["MD"], axis =1)
    df = df.drop(["Location"], axis =1)

    #reset indices after dropping rows
    df = df.reset_index().drop(["index"], axis=1)

    #create a new column in the dataframe indicating event type (IMNT, conformal, VISM, or TBI)
    types = ["" for x in range(len(df.index))]
    for index, row in df.iterrows():
        if row["Desc."] == "Neutrons TC":
            if row["Notes"].find("IMNT") == -1:
                types[index] = "Conformal"
            elif row["Notes"].find("VSIM") == 1:
                types[index] = "VSIM"
            else:
                types[index] = "IMNT"
        elif row["Desc."] == "Verify Sim":
            types[index] = "VSIM"
        elif row["Desc."] == "Sim No Charge":
            types[index] = "TBI"
        else:
            types[index] == "Unknown"

    df["Type"] = types

    #drop unnecessary columns
    df = df.drop(["Notes"], axis =1)
    df = df.drop(["Desc."], axis =1)

    return df

if __name__ == '__main__':
    allEvents = grabEvents()
    main(allEvents)