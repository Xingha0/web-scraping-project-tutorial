import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

from bs4 import BeautifulSoup
import requests
import sqlite3
import matplotlib.pyplot as plt

import pandas as pd

# Define the URL
url = "https://ycharts.com/companies/TSLA/revenues"

# Set up more headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1"  # Do Not Track request header
}

# Use a session to maintain cookies and headers across requests
session = requests.Session()
session.headers.update(headers)

# Send the GET request with the session
response = session.get(url)

# Check if the request was successful
if response.status_code == 200:
    html_content = response.text
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all tables
    tables = soup.find_all('table')
    
    # The first table is the relevant one
    quarterly_table = tables[0]

    # Extract headers
    headers = [header.text for header in quarterly_table.find_all('th')]

    # Extract rows
    rows = []
    for row in quarterly_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 0:  # Skip headers
            row_data = [cell.text.strip() for cell in cells]
            rows.append(row_data)
            
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)

# Create a DataFrame
df = pd.DataFrame(rows, columns=headers)

# Verify by printing the DataFrame
print(df)

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Convert 'Value' column to float
df['Value'] = df['Value'].replace({'B': ''}, regex=True).astype(float)

df.drop(columns=['Value'])

# Create an empty SQLite database and connect to it
conn = sqlite3.connect('tesla_revenue.db')
cursor = conn.cursor()

# Create the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS revenue (
        date TEXT,
        value REAL
    )
''')
conn.commit()

# Insert the values
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO revenue (date, value)
        VALUES (?, ?)
    ''', (row['Date'].strftime('%Y-%m-%d'), row['Value']))
conn.commit()

# Close the connection
conn.close()

# Line plot for revenue over time
plt.figure(figsize=(10, 5))
plt.plot(df['Date'], df['Value'], marker='o', linestyle='-', color='b')
plt.title('Quarterly Revenue Over Time')
plt.xlabel('Date')
plt.ylabel('Revenue (Billion USD)')
plt.grid(True)
plt.show()

# Bar plot for revenue comparison
plt.figure(figsize=(10, 5))
plt.bar(df['Date'], df['Value'], color='green')
plt.title('Quarterly Revenue Comparison')
plt.xlabel('Date')
plt.ylabel('Revenue (Billion USD)')
plt.xticks(rotation=90)
plt.grid(True)
plt.show()

# Scatter plot for revenue distribution
plt.figure(figsize=(10, 5))
plt.scatter(df['Date'], df['Value'], color='red')
plt.title('Quarterly Revenue Distribution')
plt.xlabel('Date')
plt.ylabel('Revenue (Billion USD)')
plt.grid(True)
plt.show()