Distributed Github crawler based on Python, Docker and https://developer.github.com/v3/


## Master node

```bash
cd master
```

Build the master node

```bash
docker build -t hugodelval/github-crawler-master .
```

Then, let's choose an IP address for the master.

```bash
master_ip=192.168.0.73
```

Run the master node

```bash
docker run -i -p ${master_ip}:5000:5000 hugodelval/github-crawler-master
```


## Slave node

```bash
cd slave
```

Build the slave node

```bash
docker build -t hugodelval/github-crawler-slave .
```

Run some slaves nodes

```bash
docker run -i -p 0.0.0.0:5001:5001 hugodelval/github-crawler-slave python3 /app/slave.py ${master_ip} 5001
docker run -i -p 0.0.0.0:5002:5002 hugodelval/github-crawler-slave python3 /app/slave.py ${master_ip} 5002
```
