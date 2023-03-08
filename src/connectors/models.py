from src import db

class Connectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    worker_host = db.Column(db.String(20))
    worker_port = db.Column(db.Integer)