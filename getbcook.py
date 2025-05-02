import sqlite3
import os
import shutil

# Path to Brave's Cookies database
brave_profile_path = os.path.expanduser('~/Library/Application Support/BraveSoftware/Brave-Browser/Default')
cookies_db_path = os.path.join(brave_profile_path, 'Cookies')

# Copy the database to avoid lock issues
copied_db_path = os.path.join('/tmp', 'Cookies')
shutil.copy2(cookies_db_path, copied_db_path)

# Connect to the copied database
conn = sqlite3.connect(copied_db_path)
cursor = conn.cursor()

# Query to select cookies
cursor.execute("SELECT host_key, name, value, path, expires_utc FROM cookies")

# Display cookies
for host_key, name, value, path, expires_utc in cursor.fetchall():
    print(f"Host: {host_key}, Name: {name}, Value: {value}, Path: {path}, Expires: {expires_utc}")

# Close the connection
conn.close()
