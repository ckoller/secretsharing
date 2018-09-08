from app.api.ceps import module
import config, json, requests, numpy as np
from flask import request

@module.route('/share/', methods=['GET', 'POST'])
def share():
    if request.method == 'POST':
        share = json.loads(request.form['share'])
        gate_id = json.loads(request.form['gate_id'])
        config.protocol.handle_input_share(share, gate_id)
    return "share"



