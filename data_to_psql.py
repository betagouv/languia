import os
import traceback
import json
from psycopg2 import sql
import psycopg2
from datetime import datetime

# Database connection parameters
DB_CONNECTION = os.getenv("DB_CONNECTION")

# Directory containing the JSON files
json_directory = "./data/s3"
# json_directory = os.getenv("LOGDIR") or "./data"

# Connect to PostgreSQL

conn = psycopg2.connect(dsn=DB_CONNECTION)
cur = conn.cursor()
print("Successfully connected to the database")

# Create the conversation_logs table if it doesn't exist
cur.execute(
    """
CREATE TABLE IF NOT EXISTS conversation_logs (
    id SERIAL PRIMARY KEY,
    tstamp TIMESTAMP,
    type TEXT,
    conv_id TEXT UNIQUE,
    models TEXT,
    state_a JSONB,
    state_b JSONB,
    ip TEXT,
    details JSONB
);
"""
)

# Create the logs table if it doesn't exist
cur.execute(
    """
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    tstamp TIMESTAMP,
    msg JSONB
);
"""
)
    # Loop through each JSON file in the directory
for filename in os.listdir(json_directory):
    if filename.endswith(".json") and filename.startswith("conv-"):
        file_path = os.path.join(json_directory, filename)

        with open(file_path, "r") as file:
            for line in file:
                try: 
                    data = json.loads(line)

                    if data.get("type") not in ["leftvote","rightvote","bothbad"]:
                        if data.get("type") != "chat":
                            print("Ignoring event "+data.get("type"))
                        continue

                    # Prepare SQL INSERT statement
                    insert_query = sql.SQL(
                        """
                    INSERT INTO conversation_logs (tstamp, type, conv_id, models, state_a, state_b, ip, details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    )

                    def build_conv_id(data):
                        conv_state = data.get("conversations_state", None)
                        if conv_state:
                            return conv_state[0].get("conv_id", None)+"-"+conv_state[1].get("conv_id", None)
                        # elif data.get("state", None):
                        #     return data.get("state", None).get("conv_id", None)
                        else:
                            return None

                    states = data.get("conversations_state", {})
                    # Extract values from JSON
                    tstamp = datetime.fromtimestamp(data.get("tstamp"))
                    type_ = data.get("type")
                    conv_id = build_conv_id(data)
                    models = data.get("models", None)
                    # model = data.get("model", None)
                    state_a = json.dumps(states[0])
                    state_b = json.dumps(states[1])
                    ip = data.get("ip", None)
                    details = json.dumps(data.get("details", {}))

                    # Execute the insert statement
                    cur.execute(
                        insert_query,
                        (
                            tstamp,
                            type_,
                            conv_id,
                            models,
                            state_a,
                            state_b,
                            ip,
                            details,
                        ),
                    )
                    print("Data successfully parsed")

                except Exception as e:
                    print(f"An error occurred: {e}")
                    print(traceback.format_exc())
                    # 
                    

# Commit changes and close the connection
conn.commit()

# Create the logs table if it doesn't exist
cur.execute(
    """
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    tstamp TIMESTAMP,
    data JSONB
);
""")
for filename in os.listdir(json_directory):
    if filename.endswith(".jsonl") and filename.startswith("logs-"):
        file_path = os.path.join(json_directory, filename)

        with open(file_path, "r") as file:
            for line in file:
                try: 
                    tstamp = datetime.fromtimestamp(data.get("tstamp"))
                    data = json.loads(line)

                    # Prepare SQL INSERT statement
                    insert_query = sql.SQL(
                        """
                    INSERT INTO logs (tstamp, msg)
                    VALUES (%s, %s);
                    """
                    )

                    # Execute the insert statement
                    cur.execute(
                        insert_query,
                        (
                            tstamp,
                            data,
                        ),
                    )
                    print("Data successfully parsed")

                except Exception as e:
                    print(f"An error occurred: {e}")
                    print(traceback.format_exc())
                    # continue

# Commit changes and close the connection
conn.commit()
print("All data successfully committed into the database")

# finally:
if cur:
    cur.close()
if conn:
    conn.close()
print("Database connection closed")
