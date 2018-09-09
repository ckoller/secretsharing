from app.api.ceas import module
import config
import json
import numpy as np
from flask import request
from app.api.ceas.commitment import Commitment

@module.route('/commit/<int:id>/accusation/', methods=['POST', 'PUT'])
def accuse(id):
    accusation = request.form['accusation']
    sender_id = json.loads(request.form['sender_id'])
    prover_id = json.loads(request.form['prover_id'])
    commit_id = json.loads(request.form['commit_id'])
    commitment = get_commitment(prover_id, commit_id)
    if request.method == 'POST':
        commitment.handle_con_accusation(accusation, sender_id)
    elif request.method == 'PUT':
        cid, pid, share = commitment.handle_share_accusation(accusation, sender_id)
    return "HELLO ADD" + str(id)

@module.route('/commit/<int:id>/dispute/', methods=['POST'])
def dispute(id):
    if request.method == 'POST':
        status = request.form['status']
        disputes = json.loads(request.form['disputes'])
        sender_id = json.loads(request.form['sender_id'])
        prover_id = json.loads(request.form['prover_id'])
        commit_id = json.loads(request.form['commit_id'])
        commitment = get_commitment(prover_id, commit_id)
        commitment.handle_dispute(status, sender_id, disputes)
    return "HELLO ADD" + str(id)

@module.route('/commit/<int:id>/consistency/', methods=['POST', 'PUT'])
def consistency(id):
    if request.method == 'POST':
        consistency_value = request.form['consistency_value']
        sender_id = json.loads(request.form['sender_id'])
        prover_id = json.loads(request.form['prover_id'])
        commit_id = json.loads(request.form['commit_id'])
        commitment = get_commitment(prover_id, commit_id)
        commitment.check_con_value(consistency_value, sender_id)
    elif request.method == 'PUT':
        consistency_values = json.loads(request.form['consistency_values'])
        sender_id = json.loads(request.form['sender_id'])
        prover_id = json.loads(request.form['prover_id'])
        commit_id = json.loads(request.form['commit_id'])
        commitment = get_commitment(prover_id, commit_id)
        commitment.check_new_con_value(consistency_values)
    return "HELLO ADD" + str(id)


@module.route('/commit/', methods=['GET', 'POST', 'PUT'])
def commit():
    if request.method == 'GET':
        commit_id = get_commit_id()
        commitment = get_commitment(config.id, commit_id)
        value = int(request.args.get('value'))
        poly = commitment.commit_to_value(value)
        return ','.join(str(x) for x in poly)
    elif request.method == 'POST':
        share = np.array(json.loads(request.form['share']))
        prover_id = json.loads(request.form['prover_id'])
        commit_id = json.loads(request.form['commit_id'])
        commitment = get_commitment(prover_id, commit_id)
        commitment.share_con_values(share)
    elif request.method == 'PUT':
        shares = json.loads(request.form['shares'])
        sender_id = json.loads(request.form['sender_id'])
        prover_id = json.loads(request.form['prover_id'])
        commit_id = json.loads(request.form['commit_id'])
        commitment = get_commitment(prover_id, commit_id)
        commitment.check_share(shares)
    return "hej"

def get_commit_id():
    global commit_count
    commit_id = str(config.id) + str(commit_count)
    commit_count = commit_count + 1
    return int(commit_id)

def get_commitment(prover_id, commit_id):
    global commitments
    if commit_id not in commitments:
        commitments[commit_id] = Commitment(prover_id, commit_id)
    return commitments[commit_id]

# flask state only last as long as a request, so in order for variables to survive for longer than a single request
# we do this for now
commitments = {}
commit_count = 0

