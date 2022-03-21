from app import handler
import json

payload = {
  "name": "Alex Noboa",
  "email": "aanoboa@gmail.com",
  "location": "miami",
  "daterange": ["01/01/2022", "01/05/2022"],
  "dateunsure": False,
  "occasion": [
      "Anniversary",
      "Birthday"
      ],
  "activities": [
    "Hiking"
  ],
  "numberofadults": 1,
  "numberofkids": 0,
  "budget": 5000
}


handler(event=payload, context=None)