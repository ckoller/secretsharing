from app.api.ceps import module
import config, json, requests, numpy as np
from flask import request

@module.route('/share/', methods=['GET', 'POST'])
def handle_input_share():
    if request.method == 'POST':
        shares = json.loads(request.form['shares'])
        sender_id = json.loads(request.form['sender_id']) # TODO authentification
        config.ceps.handle_input_shares(shares)
    return "share"

@module.route('/mult_share/', methods=['GET', 'POST'])
def handle_mult_share():
    if request.method == 'POST':
        share = json.loads(request.form['shares'])
        sender_id = int(json.loads(request.form['sender_id']))
        config.ceps.handle_mult_share(share, 0, sender_id)
    return "share"

@module.route('/output_share/', methods=['GET', 'POST'])
def handle_output_share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        gate_id = int(json.loads(request.form['gate_id']))
        sender_id = int(json.loads(request.form['sender_id']))
        config.ceps.handle_output_share(share, gate_id, sender_id)
    return "share"

