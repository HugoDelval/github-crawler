from flask import Flask, jsonify
import argparse
import requests
import json
import logging

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)

master_ip = "127.0.0.1"
master_url = "http://{master_ip}:5000/{endpoint}"
REGISTER = "register"
slave_token = "None"


@app.route('/get_user', methods=["POST"])
def hello_world():
    return jsonify({"user": 'Hello World!'})


def register_to_master():
    global slave_token
    logging.info("Registering to master node at IP: " + master_ip)
    try:
        res = requests.post(master_url.format(master_ip=master_ip, endpoint=REGISTER))
        logging.debug("plop")
        logging.debug(res.text)
        data_received = json.loads(res.text)
        slave_token = data_received["token"]
    except Exception as e:
        logging.error("Error registering to master node: " + str(e))
        return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Github crawler slave.')
    parser.add_argument('master_ip', metavar='master_ip', type=str, help='The IP address of the master node')
    args = parser.parse_args()
    master_ip = args.master_ip

    if register_to_master():
        app.run("0.0.0.0", 5001)
