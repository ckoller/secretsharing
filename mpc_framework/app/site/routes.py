from . import module

@module.route('/')
def home():
    return "Welcome"