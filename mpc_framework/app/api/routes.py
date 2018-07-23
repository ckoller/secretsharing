from . import module
from jobs.tasks import add_together
import config
import json, requests
import numpy as np
from flask import request
from .commitment import Commitment



@module.route('/')
def home():
    return "HELLO WORLD"

@module.route('/add')
def subadd():
    result = add_together.delay(12, 23)
    return "HELLO ADD"


@module.route('/commit/<int:id>/consistency/', methods=['GET', 'POST'])
def consistency(id):
    if request.method == 'POST':
        consistency_value = request.form['consistency_value']
        sender_id = str(json.loads(request.form['sender_id']))
        prover_id = str(json.loads(request.form['prover_id']))
        commit_id = str(json.loads(request.form['commit_id']))
        commitment = get_commitment(prover_id, commit_id)
        #commitment.check_con_value(consistency_value, sender_id)
        print("foo")
    return "HELLO ADD" + str(id)


@module.route('/commit/', methods=['GET', 'POST'])
def commit():
    if request.method == 'GET':
        commit_id = get_commit_id()
        commitment = get_commitment(config.id, commit_id)
        value = int(request.args.get('value'))
        commitment.commit_to_value(value)
    elif request.method == 'POST':
        share = np.array(json.loads(request.form['share']))
        prover_id = str(json.loads(request.form['prover_id']))
        commit_id = str(json.loads(request.form['commit_id']))
        commitment = get_commitment(prover_id, commit_id)
        commitment.share_con_values(share)
        print(share)
    return "hej"


def get_commit_id():
    global commit_count
    commit_id = str(config.id) + str(commit_count)
    commit_count = commit_count + 1
    return commit_id

def get_commitment(prover_id, commit_id):
    print(commitments)
    global commitments
    if str(commit_id) not in commitments:
        commitments[commit_id] = Commitment(prover_id, commit_id)
    return commitments[commit_id]

# flask state only last as long as a request, so in order for variables to survive for longer than a single request
# we do this for now
commitments = {}
commit_count = 0

