from flask import Flask, request, jsonify
from rq import Queue
from redis import Redis
from common import *

redis_conn = Redis()
q = Queue(connection=redis_conn)

app = Flask(__name__)

@app.route('/clean', methods=['POST'])
def sus():
    credentials = {"private_key": request.form["private_key"], "secret_key":  request.form["secret_key"], "region": request.form["region"]}
    job = q.enqueue(worker, credentials, result_ttl=86400)
    return jsonify({"job": job.id})

@app.route('/result/<job_id>', methods=['GET'])
def get_job(job_id):
    job = q.fetch_job(job_id)
    try:
        return jsonify(job.result)
    except:
        return jsonify({"answer": "Exception"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
