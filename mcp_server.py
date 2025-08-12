# mcp_server.py
from fastapi import FastAPI, Request
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

API_URL = "https://fake-json-api.mock.beeceptor.com/users"

"""
Description:
This tool fetches user data from an external mock API (https://fake-json-api.mock.beeceptor.com/users). 
It returns a complete list of users with their information, So look for the particular string in the array of objects. Then once you find the particular any matching information, filter that particular object to get the details of that particular user. 
The data in that filtered object can be used to return any required information of the user, example: "email", "address", "zipcode".

Example usage:
- "What is email of Raquel Halvorson" -> Ans: email of the user is Flossie_Maggio@gmail.com
"""


@app.get("/users")
def get_users(search: str = ""):
    res = requests.get(API_URL)
    objects = res.json()
    filtered = []

    for obj in objects:
        name = obj.get("name", "").lower()
        if search.lower() in name:
            filtered.append(obj)

    return {"results": filtered}

# Run with: uvicorn mcp_server:app --reload
