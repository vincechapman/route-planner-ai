from redis import Redis
from rq import Queue

q = Queue('low', connection=Redis())

# from . import update_nx_stations as get_stations