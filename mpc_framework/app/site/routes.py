from . import module
import config, json, requests

@module.route('/')
def home():
    return "Welcome"

