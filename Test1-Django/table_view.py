import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('tkagg')
import sqlite3

# Retrieve data from SQLite database
conn = sqlite3.connect('video_db.db')
df = pd.read_sql_query("SELECT * FROM CountryPopulation", conn)
conn.close()

# Display table of population data
print(df)

# Create a bar graph
plt.figure(figsize=(12, 6))
plt.bar(df['country'], df['population'])
plt.xlabel('Country')
plt.ylabel('Population')
plt.title('Population by Country')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()