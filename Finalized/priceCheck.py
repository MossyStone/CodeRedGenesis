from pyspark.sql.types import FloatType
import requests
import json


#token expires every hour, must be replaced
token = 'A4VWM6KaeK0ftmoRtPPtD0VtliSi'
headers = {'Authorization': 'Bearer ' + token}

resp = requests.get('https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=SYD&destinationLocationCode=BKK&departureDate=2024-05-02&adults=1&nonStop=false&max=100' ,headers=headers)

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