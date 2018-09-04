from . import module
import config, json, requests

@module.route('/')
def home():
    return "Welcome"


@module.route('/share_test')
def add():
    url = "http://" + config.host + ":" + config.port + "/api/commit/?value=5"
    r = requests.get(url)
    return r.text

