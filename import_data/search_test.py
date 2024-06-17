import os
from opensearchpy import OpenSearch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

connection_string = os.getenv("OPENSEARCH_URI")

# Create the client with SSL/TLS enabled, but hostname verification disabled.
# client = OpenSearch(connection_string, use_ssl=True, timeout=100)

# Initialize OpenSearch client
client = OpenSearch(
    hosts=connection_string,
    use_ssl=True
)


# res = client.search(index='products', body={
#     "_source": {
#         "excludes": ["embedding"]
#     },
#     "query": {
#         "match": {
#             "description": {
#                 "query": "Shoes"
#             }
#         }
#     }
# })

res = client.search(index='products', body={
    "query": {
        "match": {
            "description": {
                "query": "shoes"
            }
        }
    }
})

print(res["hits"]["hits"][0]["_source"]["embedding"])
print(res["hits"]["hits"][0]["_source"]["name"])