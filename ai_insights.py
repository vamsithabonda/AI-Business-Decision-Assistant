from openai import OpenAI
import mysql.connector
import pandas as pd
import os


client = OpenAI(

    api_key=os.getenv("REMOVED_FOR_GITHUB"),

    base_url="https://api.groq.com/openai/v1"

)

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="businessdb"
)

query = "SELECT * FROM train"

df = pd.read_sql(query, connection)

def generate_ai_insights():

    total_sales = df["Sales"].sum()

    top_region = df.groupby("Region")["Sales"].sum().idxmax()

    top_category = df.groupby("Category")["Sales"].sum().idxmax()

    prompt = f"""

You are a professional Business Analyst.

Analyze this business data.

Total Sales: {total_sales}

Best Region: {top_region}

Best Category: {top_category}

Give output EXACTLY in this format:

## 📊Business Summary

(2-3 lines summary)

##  🎯Key Insights

- Insight 1
- Insight 2
- Insight 3

## ⚠️Risk Areas

- Risk 1
- Risk 2

## 💡Recommendations

- Recommendation 1
- Recommendation 2
- Recommendation 3

## 🚀Future Growth Ideas

- Growth Idea 1
- Growth Idea 2

Keep the response concise, professional, business-focused and easy to understand.

"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content