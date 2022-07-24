from redis import Redis
from rq import Queue

q = Queue('low', connection=Redis())