from app.api.ceps_speed import module
import config, json, requests, numpy as np
from flask import request

@module.route('/protocolRandom/share/', methods=['POST'])
def handle_protocol_random_share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        type = request.form['type']
        config.protocol.handle_protocol_random_share(share, type)
    return "share"

@module.route('/protocolDoubleRandom/share/', methods=['POST'])
def handle_protocol_double_random_share():
    if request.method == 'POST':
        share_t = json.loads(request.form['share_t'])
        share_2t = json.loads(request.form['share_2t'])
        type = request.form['type']
        config.protocol.handle_protocol_double_random_share(share_t, share_2t, type)
    return "share"

@module.route('/protocolOpen/share/', methods=['POST'])
def handle_protocol_open_share():
    if request.method == 'POST':
        shares = json.loads(request.form['shares'])
        type = request.form['type']
        config.protocol.handle_protocol_open_request(shares, type)
    return "share"

@module.route('/protocolOpen/reconstruction/', methods=['POST'])
def handle_protocol_open_answer():
    if request.method == 'POST':
        rec = json.loads(request.form['rec'])
        type = request.form['type']
        config.protocol.handle_protocol_open_answer(rec, type)
    return "share"


@module.route('/input_r/', methods=['POST'])
def handle_input_randomness():
    if request.method == 'POST':
        input_r = json.loads(request.form['input_r'])
        config.protocol.handle_input_randomness(input_r)
    return "share"

@module.route('/random_shares/', methods=['POST'])
def handle_random_preprossing_shares():
    if request.method == 'POST':
        pr_share = json.loads(request.form['pr_share'])
        pdr_share_r = json.loads(request.form['pdr_share_r'])
        pdr_share_R = json.loads(request.form['pdr_share_R'])
        config.protocol.compute_preprossing_randomness(pr_share, pdr_share_r, pdr_share_R)
    return "share"
