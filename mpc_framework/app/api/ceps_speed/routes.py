from app.api.ceps_speed import module
import config, json, requests, numpy as np
from flask import request

@module.route('/protocolRandom/share/', methods=['POST'])
def handle_protocol_random_share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        type = request.form['type']
        config.preprocessing.ceps_speed.handle_protocol_random_share(share, type)
    return "share"

@module.route('/protocolDoubleRandom/share/', methods=['POST'])
def handle_protocol_double_random_share():
    if request.method == 'POST':
        share_t = json.loads(request.form['share_t'])
        share_2t = json.loads(request.form['share_2t'])
        type = request.form['type']
        config.protocol.ceps_speed.handle_protocol_double_random_share(share_t, share_2t, type)
    return "share"

@module.route('/protocolOpen/share/', methods=['POST'])
def handle_protocol_open_share():
    if request.method == 'POST':
        shares = json.loads(request.form['shares'])
        type = request.form['type']
        config.ceps_speed.preprocessing.protocol_open.handle_request(shares, type)
    return "share"

@module.route('/protocolOpen/reconstruction/', methods=['POST'])
def handle_protocol_open_answer():
    if request.method == 'POST':
        rec = json.loads(request.form['rec'])
        type = request.form['type']
        if type == "output" or type == "alpha_beta" or type == "and" or type == "xor" or type == 'layer':
            config.ceps_speed.handle_protocol_open_answer(rec, type)
        else:
            config.ceps_speed.preprocessing.handle_protocol_open_answer(rec, type)
    return "share"


@module.route('/random_shares/', methods=['POST'])
def handle_random_preprossing_shares():
    if request.method == 'POST':
        pr_share = json.loads(request.form['pr_share'])
        pdr_share_r = json.loads(request.form['pdr_share_r'])
        pdr_share_R = json.loads(request.form['pdr_share_R'])
        config.ceps_speed.preprocessing.compute_preprossing_randomness(pr_share, pdr_share_r, pdr_share_R)
    return "share"

@module.route('/input_shares/', methods=['POST'])
def handle_input_randomness():
    if request.method == 'POST':
        r = request.form['r']
        gid = request.form['gid']
        config.ceps_speed.preprocessing.handle_random_input_shares(int(r), int(gid))
    return "share"

@module.route('/input_d_shares/', methods=['POST'])
def handle_input_share():
    if request.method == 'POST':
        d = request.form['d']
        gid = request.form['gid']
        config.ceps_speed.handle_input_share(int(d), int(gid))
    return "share"

@module.route('/input_d_dict/', methods=['POST'])
def handle_all_input_shares():
    if request.method == 'POST':
        d = json.loads(request.form['d'])
        config.ceps_speed.handle_input_share(d, 0)
    return "share"
