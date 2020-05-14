from flask_redis import FlaskRedis

"""
redis store connection handler,
init application on bootstrap.

import lib.provider.redis.store 
"""
store = FlaskRedis()
