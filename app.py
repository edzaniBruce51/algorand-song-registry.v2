from flask import Flask, render_template, request, redirect, flash
from algosdk import mnemonic, account, encoding
from algosdk.v2client import algod
from algosdk.transaction import ApplicationNoOpTxn, OnComplete, wait_for_confirmation
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-for-dev-only')  # For flash messages

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # No token needed for Algonode

# Load client
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Load deployed app ID
APP_ID = 743782532  # Your deployed smart contract ID

# Load your 24-word mnemonic from .env
mnemonic_phrase = os.getenv("ALGOWALLET_MNEMONIC")
private_key = mnemonic.to_private_key(mnemonic_phrase)
sender_address = account.address_from_private_key(private_key)


@app.route("/")
def index():
    """View all registered songs"""
    try:
        app_info = algod_client.application_info(APP_ID)
        app_state = app_info['params'].get('global-state', [])
    except Exception as e:
        flash(f"Error getting app info: {e}", "error")
        return render_template("index.html", songs=[])
    
    songs = []
    song_count = 0
    
    # Get song count
    for entry in app_state:
        try:
            key = base64.b64decode(entry['key']).decode('utf-8', errors='ignore')
            if key == "song_count":
                song_count = entry['value']['uint']
                break
        except:
            continue
    
    # Parse songs using binary key analysis
    song_data = {}
    
    for entry in app_state:
        try:
            key_bytes = base64.b64decode(entry['key'])
            
            # Check if it's a song key (starts with "song_")
            if key_bytes.startswith(b'song_') and len(key_bytes) > 5:
                # Extract the parts: song_ + 8-byte-id + _ + field
                remaining = key_bytes[5:]  # Remove "song_" prefix
                
                # Find the last underscore (separates ID from field)
                last_underscore = remaining.rfind(b'_')
                if last_underscore > 0:
                    id_bytes = remaining[:last_underscore]
                    field_bytes = remaining[last_underscore + 1:]
                    
                    # Convert 8-byte ID to integer
                    if len(id_bytes) == 8:
                        song_id = int.from_bytes(id_bytes, 'big')
                        field = field_bytes.decode('utf-8', errors='ignore')
                        
                        # Get the value
                        if entry['value']['type'] == 1:  # bytes
                            raw_value = base64.b64decode(entry['value']['bytes'])
                            
                            # Special handling for owner field (convert to Algorand address)
                            if field == 'owner' and len(raw_value) == 32:
                                try:
                                    value = encoding.encode_address(raw_value)
                                except:
                                    value = raw_value.decode('utf-8', errors='ignore')
                            else:
                                value = raw_value.decode('utf-8', errors='ignore')
                        else:  # uint
                            value = entry['value']['uint']
                        
                        # Store in our data structure
                        if song_id not in song_data:
                            song_data[song_id] = {}
                        song_data[song_id][field] = value
                        
        except Exception as e:
            continue
    
    # Build songs list from parsed data
    for song_id in sorted(song_data.keys()):
        song_info = song_data[song_id]
        if 'title' in song_info and 'url' in song_info:
            song = {
                'id': song_id,
                'title': song_info.get('title', 'Unknown'),
                'url': song_info.get('url', ''),
                'price': song_info.get('price', 0),
                'owner': song_info.get('owner', 'Unknown')
            }
            songs.append(song)
    
    return render_template("index.html", songs=songs)


@app.route("/register_song", methods=["POST"])
def register_song():
    try:
        title = request.form.get("title")
        url = request.form.get("url")
        price = int(request.form.get("price"))

        # App call with arguments
        app_args = [
            b"register_song",
            title.encode("utf-8"),
            url.encode("utf-8"),
            price.to_bytes(8, "big")
        ]

        params = algod_client.suggested_params()
        txn = ApplicationNoOpTxn(
            sender=sender_address,
            sp=params,
            index=APP_ID,
            app_args=app_args
        )

        signed_txn = txn.sign(private_key)
        tx_id = algod_client.send_transaction(signed_txn)
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        
        flash("Song registered successfully!", "success")
        
    except Exception as e:
        flash(f"Error registering song: {e}", "error")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
