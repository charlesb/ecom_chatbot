import os, json
from openai import OpenAI
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

# Define index schema
index_body = {
    'settings': {
        'index': {
            'knn': True,
            'knn.algo_param.ef_search': 100
        }
    },
    'mappings': {
        'properties': {
            'name': {'type': 'text'},
            'category': {'type': 'text'},
            'description': {'type': 'text'},
            'price': {'type': 'float'},
            'sku': {'type': 'keyword'},
            'tags': {'type': 'keyword'},
            'embedding': {
                'type': 'knn_vector',
                'dimension': 1536,  # Dimension of the embedding vector
                'method': {
                    'name': "hnsw",
                    'space_type': "l2",
                    'engine': "faiss"
                }
            }
        }
    }
}

# Create the index
client.indices.create(index='products', body=index_body)

# Load products from JSON file
with open('./import_data/products.json', 'r') as file:
    products = json.load(file)

# Initialize OpenAI client
openai = OpenAI(
    api_key=os.environ.get("MY_OPENAI_API_KEY")
)

# Function to generate embeddings
def generate_embeddings(text):
    try:
        response = openai.embeddings.create(input=[text], model="text-embedding-3-small")
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

# Index products with embeddings
for product in products:
    embedding = generate_embeddings(product['description'])
    product['embedding'] = embedding

    # Index the product into OpenSearch
    client.index(
        index='products',
        body=product,
        id=product['sku']
    )

print("Products indexed successfully with embeddings.")