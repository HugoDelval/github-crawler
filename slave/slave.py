from flask import Flask, jsonify
import argparse
import requests
import json
import logging

from flask import request

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)

master_ip = "127.0.0.1"
slave_port = 5001
slave_token, auth = "None", ("None", "None")
master_url = "http://{master_ip}:5000/{endpoint}"
REGISTER = "register"

github_url = "https://api.github.com/{endpoint}"


@app.route('/users', methods=["POST"])
def get_users():
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 20)
    url = github_url.format(endpoint=("users?page=" + page + "&per_page=" + per_page))
    logging.info("Request Github API: " + url)
    github_resp = requests.get(url, auth=auth)
    return jsonify({"users": json.loads(github_resp.text)})


@app.route('/users/<user>/repos', methods=["POST"])
def get_repos(user):
    url = github_url.format(endpoint=("users/" + user + "/repos"))
    logging.info("Request Github API: " + url)
    github_resp = requests.get(url, auth=auth)
    return jsonify({"repos": json.loads(github_resp.text)})


@app.route('/repos/<user>/<repo>/contributors', methods=["POST"])
def get_contributors(user, repo):
    url = github_url.format(endpoint=("repos/" + user + "/" + repo + "/contributors"))
    logging.info("Request Github API: " + url)
    github_resp = requests.get(url, auth=auth)
    return jsonify({"users": json.loads(github_resp.text)})


def register_to_master():
    global slave_token, auth
    logging.info("Registering to master node at IP: " + master_ip)
    try:
        res = requests.post(master_url.format(master_ip=master_ip, endpoint=REGISTER), json={"port": slave_port})
        logging.debug("plop")
        logging.debug(res.text)
        data_received = json.loads(res.text)
        slave_token = data_received["token"]
        auth = (slave_token.split(":")[0], slave_token.split(":")[1])
    except Exception as e:
        logging.error("Error registering to master node: " + str(e))
        return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Github crawler slave.')
    parser.add_argument('master_ip', metavar='master_ip', type=str, help='The IP address of the master node')
    parser.add_argument('slave_port', metavar='slave_port', type=int, help='The port where the slave node will listen')
    args = parser.parse_args()
    master_ip = args.master_ip
    slave_port = args.slave_port

    if register_to_master():
        app.run("0.0.0.0", slave_port)
