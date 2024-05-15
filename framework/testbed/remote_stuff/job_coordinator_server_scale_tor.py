import os, sys
import subprocess as sub
import logging
import time
import socket
import requests
from flask import Flask

app = Flask(__name__)

client_count = 5

# client_count = 1



@app.route('/signalTermination', methods=['POST'])
def signal_termination():
    global client_count
    client_count -= 1
    print("----- client_count: " + str(client_count))
    if client_count == 0:
        os.system("touch terminator")
    return "terminated"



if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5005)
    