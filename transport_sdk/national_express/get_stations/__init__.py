from redis import Redis
from rq import Queue

q = Queue('nx_get_stations', connection=Redis())
