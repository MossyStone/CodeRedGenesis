from openai import OpenAI
from pyspark.sql.types import FloatType
import requests
import json


client = OpenAI(
    api_key ="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"
)

# Use the Completion endpoint to generate text based on the input prompt
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Choose the GPT model
    messages=[
            {"role": "system", "content": "Extract the relevant information from the user's request and create a link like so:https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=SYD&destinationLocationCode=BKK&departureDate=2024-05-02&adults=1&nonStop=false&max=100. Convert city names to location codes. The year is 2024 by default. Use the following variable names: originLocationCode, destinationLocationCode, departureDate, returnDate, adults, children, infants, travelClass, includedAirlineCodes, nonStop, currencyCode, maxPrice, max. "},
            {"role": "user", "content": "I want to fly from London to Paris in next 2 days, get me the cheapest fare."}
            ]
)

print(response.choices[0])

amadeusLink = response.choices[0]


######################Amadeus API############################

#token expires every hour, must be replaced
token = 'T2UNgIIPdQGYb0GL8ac2lytFKdel'
headers = {'Authorization': 'Bearer ' + token}

resp = requests.get(amadeusLink ,headers=headers)

offers = resp.json()["data"]

#takes the "price" and "grandTotal" elements of each item and makes it a float
prices = list(map(lambda x: float(x["price"]["grandTotal"]),offers))
print(prices)

dataframe = spark.createDataFrame(prices, FloatType())
dataframe.show()

dataframe.coalesce(1).write.format("com.databricks.spark.csv").mode('overwrite').option("header", "true").save("dbfs:/FileStore/df/df/csv")

dataframe_read = (spark.read
    .format("csv")
    .option("mode", "PERMISSIVE")
    .load("dbfs:/FileStore/df/df/csv")
)

print("DATABRICKS FileStore READ OUTPUT")
dataframe_read.show()




#system_response = response.choices[0].message['system']['content']
#print("System Response:", system_response)


"""
response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "Given a user’s request, store keywords about flight information in python variables.;"
    },
    {
      "role": "user",
      "content": f"I want the {3} cheapest flights from {Houston} to {Berlin}. My departure is {tomorrow}."
    }
  ],
  temperature=0.7,
  max_tokens=64,
  top_p=1
)
"""
