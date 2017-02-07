# Distributed Github crawler 

Based on Python Flask, Docker and https://developer.github.com/v3/


## Master node

```bash
cd master
```

Build and push the master node (for developers)

```bash
docker build -t hugodelval/github-crawler-master .
docker push hugodelval/github-crawler-master
```

Then, let's choose an IP address for the master.

```bash
master_ip=192.168.0.73
```

Run the master node

```bash
docker run -i -p ${master_ip}:5000:5000 hugodelval/github-crawler-master
```

The master will ask you to enter a Github username and an authentication token (from [https://github.com/settings/tokens](github.com/settings/tokens)).
The wanted string looks like ```HugoDelval:a5e855f84fa3bca2```. This Oauth token is used to access th Github API.

### Security note

Note that for now the previously entered Oauth token is passed from the master to the slaves via HTTP (and not HTTPs). So the application is not safe to use in a public cloud environment.


## Slave node

```bash
cd slave
```

Build and push the slave node (for developers)

```bash
docker build -t hugodelval/github-crawler-slave .
docker push hugodelval/github-crawler-slave
```

Run some slaves nodes

```bash
docker run -i -p 0.0.0.0:5001:5001 hugodelval/github-crawler-slave python3 /app/slave.py ${master_ip} 5001
docker run -i -p 0.0.0.0:5002:5002 hugodelval/github-crawler-slave python3 /app/slave.py ${master_ip} 5002
```

## Registering slaves and error handling

The master node keep in memory all the slaves that has been linked to him. At each request that the master makes to his slaves (for example to answer a user request), it updates its slaves' list depending of which slave node answer and how fast. This way the master node always has a list of up-to-date slaves that will efficiently answer its requests.

## The API

The master node exposes a *REST API* which allows one to request and crawl github repositories and users.

* /

    Return the list of all the available entry points with a short description
* /users?nb=nb_users_to_show
    
    Return a list of the last signed up users
    
    nb_users_to_show: integer, the number of users to show
