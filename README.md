<h1 align="center">
  <br>
  Kafka Connect Flask
  <br>
</h1>


<h4 align="center">A Minimal Flask Webapp for Kafka Connect</h4>



<p align="center">
  <a href="#key-features">Important Notes </a> •
  <a href="#key-features">How to run </a> •
  <a href="#key-features">Key Features</a> •
</p>

## Important Notes

The graphical interface is pretty minimalistic. you can add a connector by passing the connector's name, 
the worker FQDN or IP and the REST API port. Your connector will be added to the database and you will be
ready to manage it. Right now you can:

1) Connector's and tasks status
2) Configuration download
3) Stop
4) Pause
5) Resume
6) Update/Publish config
7) Delete a connector
8) Visualize tasks status as well restart them

## How to run

The process to build a docker image is traitforward because has already been done.

```bash
$ docker build -t kafka_connet_webapp .
$ docker run -d -p 8000:8000 kafka_connet_webapp
```

## Key Features

* Minimal Web Interface
* Basic Kconnect management with no need of 3th party tools or Kconnect REST
* Fully portable thanks to docker (On K8s as well)

---

> GitHub [@SomTamPhed](https://github.com/) &nbsp;&middot;&nbsp;
> Twitter [@WasamiKirua](https://twitter.com/)

