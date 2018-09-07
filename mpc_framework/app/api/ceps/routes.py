from app.api.ceps import module
import config, json, requests, numpy as np
from app.api.polynomials import Polynomials
from flask import request



@module.route('/share/', methods=['GET', 'POST'])
def share():
    share_type = "input"
    if request.method == 'GET':
        value = int(request.args.get('value'))
        config.protocol.share_value(value, "input")
    elif request.method == 'POST':
        share = json.loads(request.form['share'])
        sender_id = json.loads(request.form['sender_id'])
        share_type = request.form["share_type"]
        config.protocol.set_share(sender_id, share, share_type)
    if config.protocol.received_all_shares(share_type):
            if share_type == "input":
                config.protocol.add_all()
            elif share_type == "output":
                print(config.protocol.reconstruct(config.protocol.output_shares)[1], "res")
    return "share"



