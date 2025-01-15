import json

import json

def save_json(json_path, data):
    with open(json_path, "w") as file:
        json.dump(data, file, indent=4)

def load_json(json_path):
    try:
        with open(json_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:  # If there's a JSON error, return an empty dictionary
        print(f"Warning: {json_path} contains invalid JSON. Returning empty data.")
        return {}  # Return empty dictionary in case of error
    except FileNotFoundError:  # If the file doesn't exist, return an empty dictionary
        print(f"Warning: {json_path} not found. Creating a new file.")
        return {}  # Return empty dictionary for new file

def update_chat_data(json_path, new_data):
    # Load existing data from chats.json
    chats = load_json(json_path)
    
    # Extract username and history from the new data
    username = new_data["username"]
    new_history = new_data["history"]
    
    # Check if history is empty
    if not new_history:
        print("Warning: Provided history is empty. No updates will be made.")
        return  # If history is empty, do not update
    
    # Check if the timestamp is available in history
    if "timestamp" not in new_history[0]:
        print("Warning: Missing timestamp in history. Cannot add createdAt.")
        created_at = "Unknown"  # Fallback timestamp
    else:
        created_at = new_history[0]["timestamp"]

    # Check if the username already exists in the chats data
    if username in chats:
        # If the user exists, append the new history
        for key, value in chats[username].items():
            value["messages"].extend(new_history)
    else:
        # If the user does not exist, add a new entry
        chats[username] = {}
        chats[username][new_data["query"]] = {
            "createdAt": created_at,  # Add timestamp or fallback value
            "messages": new_history
        }
    
    # Save the updated data back to the JSON file
    save_json(json_path, chats)