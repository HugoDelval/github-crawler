import json
import random
import string

from flask import Flask
from flask import request, jsonify
import grequests
from SlaveData import SlaveData
import logging

app = Flask(__name__)
logging.getLogger().setLevel(logging.DEBUG)

slaves = [SlaveData("192.168.0.2", "false slave", 5001)]  # to show error handling -> the first request will
                                                             # eliminate  the inactive slave
slave_url = "http://{slave_ip}:{port}/{endpoint}"
GET_USER = "get_user"


def get_random_str(N):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N))


def slave_exception_handler(slave_request, exc):
    global slaves
    slave_ip = slave_request.url.split("/")[2].split(":")[-2]
    logging.info("Removing slave with IP: " + slave_ip + "\n" + " "*10 + "Because of exception: " + str(exc))
    slaves = [s for s in slaves if s.ip != slave_ip]


@app.route('/register', methods=["POST"])
def register():
    content = request.get_json()
    slave_ip = request.remote_addr
    generated_token = get_random_str(20)
    logging.info("Registering slave with IP: " + slave_ip)
    slaves.append(SlaveData(slave_ip, generated_token, content.get("port", 5001)))
    return jsonify({"token": generated_token})


@app.route('/sample', methods=["GET"])
def get_users():
    slaves_requests = [grequests.post(slave_url.format(slave_ip=s.ip, endpoint=GET_USER, port=s.port), timeout=2) for s in slaves]
    logging.info("Sending + " + GET_USER + " request to " + str(len(slaves_requests)) + " slaves.")
    resps = grequests.map(slaves_requests, size=6, exception_handler=slave_exception_handler)
    resp = list(filter(lambda u: u, map(lambda r: json.loads(r.text) if r else None, resps)))
    return jsonify({"users": resp})


if __name__ == '__main__':
    app.run("0.0.0.0", 5000)
