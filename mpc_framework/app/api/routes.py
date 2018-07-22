from . import module
from jobs.tasks import add_together


@module.route('/')
def home():
    return "HELLO WORLD"


@module.route('/add')
def subadd():
    result = add_together.delay(12, 23)
    return "HELLO ADD"


