from openai import OpenAI
client = OpenAI(
    api_key ="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"
)

# Use the Completion endpoint to generate text based on the input prompt
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Choose the GPT model
    messages=[
            {"role": "system", "content": "Extract the relevant information from the user's request and create a link like so:https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=SYD&destinationLocationCode=BKK&departureDate=2024-05-02&adults=1&nonStop=false&max=100. Convert city names to location codes. The year is 2024 by default. Use the following variable names: originLocationCode, destinationLocationCode, departureDate, returnDate, adults, children, infants, travelClass, includedAirlineCodes, nonStop, currencyCode, maxPrice, max. "},
            {"role": "user", "content": "I need the cheapest flight to go from Houston to Dallas on November 11th through November 19th."}
            ]
)

print(response.choices[0])

amadeusLink = response.choices[0]

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
