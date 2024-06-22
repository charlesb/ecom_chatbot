import redis, os, json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a customer profile
customer_profile = {
    "name": "Charles",
    "email": "charles@example.com",
    "past_transactions": ['PMRS123', 'UFYM456', 'PLDS789', 'SSTR101']
}

service_uri = os.getenv("REDIS_URI")
redis_client = redis.from_url(service_uri)

key = '551dfc94-764a-4839-b8db-e6f04b5715c6'
# key = 'foobarbaz'

redis_client.set(key, json.dumps(customer_profile))
value = json.loads(redis_client.get(key).decode('utf-8'))
# value = redis_client.get(key)

print(f"The value of {key} is:", value)

# Delete the key
# redis_client.delete(key)

# Get all key value pairs
# print(redis_client.keys())
