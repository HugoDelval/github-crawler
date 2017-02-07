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

slaves = []
# slaves.append(SlaveData("192.168.0.2", 5001))  # to show error handling -> the first request will
                                               # eliminate  the inactive slave
                                               # uncomment this line to show error handling in action
slave_url = "http://{slave_ip}:{port}/{endpoint}"
USER = "users?page={page_nb}&per_page={nb_per_page}"
REPOS = "users/{user}/repos"
CONTRIBUTORS = "repos/{repo}/contributors"


def slave_exception_handler(slave_request, exc):
    global slaves
    slave_ip = slave_request.url.split("/")[2].split(":")[-2]
    logging.info("Removing slave with IP: " + slave_ip + "\n" + " "*10 + "Because of exception: " + str(exc))
    slaves = [s for s in slaves if s.ip != slave_ip]


def distributed_request(method, endpoints, **kwargs):
    slaves_requests = []
    for i in range(len(endpoints)):
        s = slaves[i % len(slaves)]
        slaves_requests.append(grequests.request(method=method, url=slave_url.format(slave_ip=s.ip, endpoint=endpoints[i], port=s.port), timeout=30, **kwargs))
    resps = grequests.map(slaves_requests, size=6, exception_handler=slave_exception_handler)
    resp = list(filter(lambda u: u, map(lambda r: json.loads(r.text) if r else None, resps)))
    return resp


@app.route('/register', methods=["POST"])
def register():
    content = request.get_json()
    slave_ip = request.remote_addr
    logging.info("Registering slave with IP: " + slave_ip)
    slaves.append(SlaveData(slave_ip, content.get("port", 5001)))
    return jsonify({"token": passwd})


@app.route('/users', methods=["GET"])
def get_users():
    nb_users = int(request.args.get('nb', 20))
    logging.info("Sending " + USER + " request to " + str(len(slaves)) + " slaves.")
    endpoints = []
    for n in range(1, nb_users+1, 20):
        endpoints.append(USER.format(page_nb=(1+n//20), nb_per_page=20))
    users = []
    for us in distributed_request("POST", endpoints):
        users += us["users"]
    return jsonify({"users": users})


def find_close_contributors_depth(users, depth):
    if depth == 0:
        return users
    # step 1: get repos for each user
    endpoints_repo = [REPOS.format(user=u) for u in users]
    repos = []
    for rs in distributed_request("POST", endpoints_repo):
        repos += rs["repos"]
    logging.info("Got this much repos: " + str(repos))
    # step 2: get contributors for each repo
    endpoints_contribs = [CONTRIBUTORS.format(repo=r["full_name"]) for r in repos]
    users_found = []
    for user in distributed_request("POST", endpoints_contribs):
        users_found += user["users"]
    for u in users_found:
        users.add(u["login"].lower())
    # seep 3: redo
    return find_close_contributors_depth(users, depth-1)


@app.route('/contributors', methods=["GET"])
def find_close_contributors():
    user = request.args.get('user', "hugodelval").lower()
    depth = int(request.args.get('depth', 1))
    close_contributors = find_close_contributors_depth({user}, depth)
    return jsonify({"close_contributors": list(close_contributors)})


if __name__ == '__main__':
    import getpass
    passwd = getpass.getpass("Please paste your username and your OAuth access token (from "
                             "https://github.com/settings/tokens) in the form username:token, "
                             "e.g. : 'HugoDelval:a5e855f84fa3bca2' : "
                             )
    app.run("0.0.0.0", 5000)
