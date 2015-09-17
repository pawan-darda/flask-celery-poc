from __future__ import absolute_import

import celery_config
import json
from celery import Celery

from flask import Flask, Blueprint, abort
from flask import jsonify, request, session
from os import path, environ

app = Flask(__name__)
app.config.from_object(celery_config)

def make_celery(app):
    c = Celery(app.import_name,
               broker=app.config['CELERY_BROKER_URL'],
               backend=app.config['CELERY_RESULTS_URL'])
    c.conf.update(app.config)
    TaskBase = c.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    c.Task = ContextTask
    return c

celery_app = make_celery(app)

@celery_app.task(name='tasks.add')
def add(x, y):
    return x + y

@celery_app.task(name='tasks.mul')
def mul(x, y):
    return x * y

@celery_app.task(name='tasks.sub')
def xsum(numbers):
    return sum(numbers)

@app.route("/test")
def test_celery(x=16, y=16):
    x = int(request.args.get("x", x))
    y = int(request.args.get("y", y))
    res = add.l((x, y))
    context = {"id": res.task_id, "x": x, "y": y}
    result = "add((x){}, (y){})".format(context['x'], context['y'])
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)

@app.route("/test/result/<task_id>")
def show_result(task_id):
    ret_val = add.AsyncResult(task_id).get(timeout=1.0)
    return repr(ret_val)

if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
