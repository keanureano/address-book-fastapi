import requests
import json


# create a new client that will transact to my address book api
response = requests.get("http://localhost:8000/api/addresses")

# retrieve all addresses
addresses = response.json()["notes"]

# filter all addresses that has a longitude greater than 122
filtered_addresses = [
    address for address in addresses if address["longitude"] >= 122]

# print out filtered addresses
print(filtered_addresses)
