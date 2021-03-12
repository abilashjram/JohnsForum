import os
from huey import RedisHuey
import random
#worker thread

huey = RedisHuey(url=(os.getenv(('REDIS_URL'))))

#task
@huey.task(retries=5,retry_delay=10)
def get_random_num():
    print("This is a task to get a random number")
    num = random.randint(1,10)
    print("Random Number is : ", str(num))

    if num < 5:
        return True
    else :
        raise Exception("Error in worker!!")


