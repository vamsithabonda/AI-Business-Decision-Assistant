import mysql.connector
import pandas as pd

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="businessdb"
)

query = "SELECT * FROM train"

df = pd.read_sql(query, connection)

print(df.head())