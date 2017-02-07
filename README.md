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
The wanted string looks like ```HugoDelval:a5e855f84fa3bca2```. This Oauth token is used to access the Github API.

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

* /users?nb=<nb_users_to_show>
    
    Return a list of the last signed up users
    
    *nb_users_to_show*: integer, the number of users to show

* /contributors?user=<the_user>&depth=<wanted_depth>

    Return a list of users. We check all the repositories of <the_user> and look for all the contributors in these repositories. We repeat the process for each contributors a number <depth> times. This output the **close_contributors** of <the_user>
    
    *the_user*: string, login of the user you want to know the close contributors
    
    *depth*: how far do we check for contributors
    
    **Note** An output of this request is provided in the *output/* folder. This output has been generated in 3min using 3 slaves.
    
