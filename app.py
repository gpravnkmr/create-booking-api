import sys
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

def handler(event, context):
    '''
    This event handler will trigger 2 synchronous actions:
    1) POST createTrip to Travefy
    2) POST createTripUser to Travefy

    The event object represents the json input that will be parsed and passed to our handler functions
    The context object represents all system methods made available from AWS
    '''

    # 1.0 Create POST request object for createTrip
    def createTrip(event):
        '''
        Constructs a payload for a Travefy Itinerary object and POSTs it to the Create Trip endpoint
        It takes in the event object from the AWS Lambda event handler
        '''

        # 1.1 Define request objects for createTrip api call
        headers = {
            "X-USER-TOKEN": 'c4c6a2b93e184e3f99aa017d9d8ef7d6',
            "X-API-PUBLIC-KEY": 'd480edc6652b44c0879482db7030c3dd',
            "Content-Type": "application/json",
        }

        payload = json.dumps({
            "Name": f"Trip to {event['location']} for {event['first_name']} {event['last_name']}",
            "InviteMessage": f"<p>Traveler Name: {event['first_name']} {event['last_name']}<br />Traveler Email: {event['email']}<br />Location: {event['location']}<br />Dates: {event['daterange']}<br />Unsure of dates?: {event['dateunsure']}<br />Occasion: {event['occasion']}<br />Activities: {event['activities']}<br />Adults: {event['numberofadults']}<br />Kids: {event['numberofkids']}<br />Budget: {event['budget']}<br />Additional Notes: {event['notes']}<br /></p>",
            "TripCoverPhotoUrl": "http://lorempixel.com/640/480/city",
            "SeconaryLogoUrl": "https://travefy.com/content/app/images/logo.png",
            "EstimatedCost": event['budget'],
            "IsCostPerPerson": True,
            "PartnerIdentifier": f"trip-{int(time.time())}",
            "Status": "Quote",
            "IsChatDisabled": False,
            "IsPdfEnabled": False,
            "IsAppEnabled": True,
        })

        # 1.2 Send POST request to Travefy and store response for the Step 2 api call
        req = requests.post(url="https://api.travefy.com/api/v1-20190212/trips", headers=headers, data=payload)
        print(f"createTrip status code: {req.status_code}")
        booking = req.json()

        return booking


    # 2.0 Create POST request object for createTripUser
    def createTripUser(booking_response, event):
        '''
        Constructs a payload for a Travefy Trip User object and POSTs it to the Create Trip User endpoint
        It takes in the booking response output from the Create Trip response json object
        '''

        # # 2.1 Define request objects for createTripUser api call
        url = f"https://api.travefy.com/api/v1-20190212/trips/{booking_response['Id']}/tripUsers/invite"
        print(f"Booking ID is {booking_response['Id']}")
        headers = {
            "X-USER-TOKEN": 'c4c6a2b93e184e3f99aa017d9d8ef7d6',
            "X-API-PUBLIC-KEY": 'd480edc6652b44c0879482db7030c3dd',
            "X-TRIP-ID": str(booking_response['Id']),
            "Content-Type": "application/json",
        }

        payload = json.dumps({
            "tripUsers": [
                {
                    "email": event['email'],
                    "fullName": f"{event['first_name']} {event['last_name']}",
                    "role": 0,
                }
            ]
        })

        # # 2.2 Send POST request to Travefy and store response
        req = requests.post(url=url, headers=headers, data=payload)
        print(f"createTripUser status code: {req.status_code}")
        trip_user = req.json()

        return trip_user

    # Loading the event payload as a JSON body -> resolve AWS TypeError issues when parsing payload
    data = json.loads(event['body'])

    # Executting functions
    booking_response = createTrip(data)
    trip_user_response = createTripUser(booking_response, data)

    # Basic Lambda Function Logging
    print(f"Function: {context.function_name} {context.function_version} | {context.invoked_function_arn}")
    print(f"AWS Request ID: {context.aws_request_id}")
    print(f"Please check CloudWatch logging for group -> {context.log_group_name} stream -> {context.log_stream_name} for additional logging")

    # Send API response details back to event trigger
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": {
            "bookingResponse": json.dumps(booking_response),
            "tripUserResponse": json.dumps(trip_user_response)
            }
    }