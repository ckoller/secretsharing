from app.api.ceps import module
from jobs.tasks import add_together
import config, json, requests, numpy as np
from app.api.polynomials import Polynomials
from flask import request
from app.api.ceas.commitment import Commitment

@module.route('/share/', methods=['GET', 'POST'])
def share():
    if request.method == 'GET':
        value = int(request.args.get('value'))
        pol = Polynomials()
        poly, shares = pol.create_poly_and_shares(value, degree=config.player_count/3, shares=config.player_count)
        for player_id, player in config.players.items():
            url = "http://" + player + "api/ceps/share"
            data = {"share": json.dumps(shares[player_id]),
                    "sender_id": config.my_id,
                    "share_id": get_share_id()}
            requests.post(url, data)
            return shares[int(config.my_id)]
    elif request.method == 'POST':
        share = np.array(json.loads(requests.form("share")))
        share_id = np.array(json.loads(requests.form("share_id")))
        sender_id = json.loads(requests.form("sender_id"))
        get_share(sender_id, share_id, share)
    return "share"

@module.route("/share/", methods=['GET', 'POST'])
def add():
    # add((add(p1,p2), p2)
    if request.method == 'GET':
        val1 = int(request.args.get('player_id1'))
        val2 = int(request.args.get('player_id2'))
        


        pol = Polynomials()
        poly, shares = pol.create_poly_and_shares(value, degree=config.player_count/3, shares=config.player_count)
        for player_id, player in config.players.items():
            url = "http://" + player + "api/ceps/share"
            data = {"share": json.dumps(shares[player_id]),
                    "sender_id": config.my_id,
                    "share_id": get_share_id()}
            requests.post(url, data)
            return shares[int(config.my_id)]
    elif request.method == 'POST':
        share = np.array(json.loads(requests.form("share")))
        share_id = np.array(json.loads(requests.form("share_id")))
        sender_id = json.loads(requests.form("sender_id"))
        get_share(sender_id, share_id, share)
    print("a + b")

def get_share_id():
    global share_count
    share_id = str(config.id) + str(share_count)
    share_count = share_count + 1
    return int(share_id)

def get_share(owner_id, share_id, share):
    global share_dict
    if share_id not in share_dict:
        share_dict[share_id] = {owner_id, share}
    return share_dict[share_id]

# flask state only last as long as a request, so in order for variables to survive for longer than a single request
# we do this for now
share_dict = {}
share_count = 0
