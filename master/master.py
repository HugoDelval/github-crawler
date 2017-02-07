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
passwd = "username:access_token_from_https://github.com/settings/tokens"

slaves = [SlaveData("192.168.0.2", 5001)]  # to show error handling -> the first request will
                                           # eliminate  the inactive slave
slave_url = "http://{slave_ip}:{port}/{endpoint}"
GET_USER = "get_user"


def slave_exception_handler(slave_request, exc):
    global slaves
    slave_ip = slave_request.url.split("/")[2].split(":")[-2]
    logging.info("Removing slave with IP: " + slave_ip + "\n" + " "*10 + "Because of exception: " + str(exc))
    slaves = [s for s in slaves if s.ip != slave_ip]


@app.route('/register', methods=["POST"])
def register():
    content = request.get_json()
    slave_ip = request.remote_addr
    logging.info("Registering slave with IP: " + slave_ip)
    slaves.append(SlaveData(slave_ip, content.get("port", 5001)))
    return jsonify({"token": passwd})


@app.route('/sample', methods=["GET"])
def get_users():
    slaves_requests = [grequests.post(slave_url.format(slave_ip=s.ip, endpoint=GET_USER, port=s.port), timeout=2) for s in slaves]
    logging.info("Sending + " + GET_USER + " request to " + str(len(slaves_requests)) + " slaves.")
    resps = grequests.map(slaves_requests, size=6, exception_handler=slave_exception_handler)
    resp = list(filter(lambda u: u, map(lambda r: json.loads(r.text) if r else None, resps)))
    return jsonify({"users": resp})


if __name__ == '__main__':
    import getpass
    passwd = getpass.getpass("Please paste your username and your OAuth access token (from "
                             "https://github.com/settings/tokens) in the form username:token, "
                             "e.g. : 'HugoDelval:a5e855f84fa3bca2' : "
                             )
    app.run("0.0.0.0", 5000)
