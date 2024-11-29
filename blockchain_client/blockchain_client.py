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
@app.route('/view/transactions')
def view_transaction():
    return render_template('view_transactions.html')

if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port, debug=True)










