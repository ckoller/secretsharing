from app.api.ceps import module
import config, json, requests, numpy as np
from flask import request

@module.route('/share/', methods=['GET', 'POST'])
def handle_input_share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        gate_id = json.loads(request.form['gate_id'])
        config.ceps.handle_input_share(share, gate_id)
    return "share"

@module.route('/mult_share/', methods=['GET', 'POST'])
def handle_mult_share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        gate_id = json.loads(request.form['gate_id'])
        config.ceps.handle_mult_share(share, gate_id)
    return "share"

@module.route('/output_share/', methods=['GET', 'POST'])
def handle_output_share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        config.ceps.handle_output_share(share)
    return "share"

