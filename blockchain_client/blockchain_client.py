from random import random
from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
import binascii
from collections import OrderedDict
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid
app = Flask(__name__)
CORS(app)


class FlightManager:
    def __init__(self, csv_path='flights.csv'):
        """
        Initialize FlightManager with a CSV file path
        Create the file with sample data if it doesn't exist
        """
        self.csv_path = csv_path

        # If CSV doesn't exist, create it with sample data
        if not os.path.exists(csv_path):
            self.create_initial_flights()

    def create_initial_flights(self):
        """
        Create initial sample flights and save to CSV
        """
        base_date = datetime.now() + timedelta(days=30)
        sample_flights = [
            {
                'id': 1,
                'flight_number': 'AA123',
                'airline': 'American Airlines',
                'source': 'New York (JFK)',
                'destination': 'Los Angeles (LAX)',
                'departure_time': (base_date + timedelta(days=0, hours=8)).strftime('%Y-%m-%d %H:%M'),
                'arrival_time': (base_date + timedelta(days=0, hours=11, minutes=30)).strftime('%Y-%m-%d %H:%M'),
                'price': 350.50,
                'seats_available': 150,
                'flight_duration': '5h 30m'
            },
            {
                'id': 2,
                'flight_number': 'DL456',
                'airline': 'Delta Airlines',
                'source': 'Chicago (ORD)',
                'destination': 'Miami (MIA)',
                'departure_time': (base_date + timedelta(days=1, hours=10)).strftime('%Y-%m-%d %H:%M'),
                'arrival_time': (base_date + timedelta(days=1, hours=13, minutes=15)).strftime('%Y-%m-%d %H:%M'),
                'price': 250.75,
                'seats_available': 120,
                'flight_duration': '3h 15m'
            },
            {
                'id': 3,
                'flight_number': 'UA789',
                'airline': 'United Airlines',
                'source': 'San Francisco (SFO)',
                'destination': 'Seattle (SEA)',
                'departure_time': (base_date + timedelta(days=2, hours=7)).strftime('%Y-%m-%d %H:%M'),
                'arrival_time': (base_date + timedelta(days=2, hours=8, minutes=45)).strftime('%Y-%m-%d %H:%M'),
                'price': 180.25,
                'seats_available': 100,
                'flight_duration': '1h 45m'
            }
        ]

        # Create DataFrame and save to CSV
        df = pd.DataFrame(sample_flights)
        df.to_csv(self.csv_path, index=False)
        print(f"Created initial flights CSV at {self.csv_path}")

flight_manager = FlightManager()


class Transaction:
    def __init__(self,user_name,flight_number,source,destination,date,sender_public_key,sender_private_key,
                 recipient_public_key,amount,status):
        self.booking_id = str(uuid.uuid4())
        self.sender_public_key = sender_public_key
        self.sender_private_key = sender_private_key
        self.recipient_public_key = recipient_public_key
        self.user_name = user_name
        self.flight_number = flight_number
        self.source = source
        self.destination = destination
        self.date = date
        self.amount = amount
        self.status = status
    def to_dict(self):
        return OrderedDict({
            'sender_public_key':self.sender_public_key,
            'recipient_public_key':self.recipient_public_key,
            'amount':self.amount,
            'booking_id':self.booking_id,
            'flight_number':self.flight_number,
            'user_name':self.user_name,
            'date':self.date,
            'source':self.source,
            'destination':self.destination,
            'status': self.status
        })
    def sign_transaction(self):
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/book/flight')
def book_flight():
    return render_template('bookflight.html')
@app.route('/wallet/new')
def new_wallet():
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024,random_gen)
    public_key = private_key.publickey()
    response = {
        'private_key':binascii.hexlify(private_key.exportKey(format('DER'))).decode('ascii'),
        'public_key':binascii.hexlify(public_key.exportKey(format('DER'))).decode('ascii')
    }
    return jsonify(response),200


@app.route('/fetch/flights', methods=['GET'])
def fetch_flights():
    # Get query parameters
    source = request.args.get('source')
    destination = request.args.get('destination')
    print(source, destination)

    # Read the flights CSV
    df = pd.read_csv(flight_manager.csv_path)

    # Apply filters if source and/or destination are provided
    if source and destination:
        # Filter by both source and destination
        filtered_flights = df[
            (df['source'].str.contains(source, case=False)) &
            (df['destination'].str.contains(destination, case=False))
            ]
    elif source:
        # Filter by source only
        filtered_flights = df[df['source'].str.contains(source, case=False)]
    elif destination:
        # Filter by destination only
        filtered_flights = df[df['destination'].str.contains(destination, case=False)]
    else:
        # If no filters, return all flights
        print('nothing')
        filtered_flights = df

    # Convert to list of dictionaries and return
    return jsonify(filtered_flights.to_dict('records'))


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port, debug=True)










