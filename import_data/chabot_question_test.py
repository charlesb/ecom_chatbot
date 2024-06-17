import os
from openai import OpenAI
from opensearchpy import OpenSearch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define model
EMBEDDING_MODEL = "text-embedding-3-small"

# Define the Client
openaiclient = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("MY_OPENAI_API_KEY"),
)

# Define question
# question = "I want to run occasionally, what shoes should I buy?"
question = "shoes"

# Create embedding
question_embedding = openaiclient.embeddings.create(input=question, model=EMBEDDING_MODEL)

# print(question_embedding.data[0].embedding)

connection_string = os.getenv("OPENSEARCH_URI")

client = OpenSearch(
    hosts=connection_string,
    use_ssl=True
)

response = client.search(
  index = "products",
  body = {
      "size": 3,
      "query" : {
        "knn" : {
          "embedding":{
          "vector":  question_embedding.data[0].embedding,
          "k": 3
        }
      }
    }
  }
)

for result in response["hits"]["hits"]:
  
  print("name:" + str(result["_source"]['name']))
  print("category: " + str(result["_source"]["category"]))
  print("description: " + str(result["_source"]["description"]))
  print("price: " + str(result["_source"]["price"]))

# Retrieve the text of the first result in the above dataset
top_hit_description = response['hits']['hits'][0]['_source']['description']
top_hit_name = response['hits']['hits'][0]['_source']['name']
# Craft a reply

prompt = """
You are a helpful assistant for an ecommerce webiste specialized in sporting goods.
You decline politely if the question is not related to sport or sporting goods.
You provide the user with the best product that matches their needs.
"""

response = openaiclient.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Answer the following question:" 
            + question 
            + "by using the following text:" 
            + top_hit_description
            + "and the best product for this is:"
            + top_hit_name
        }
        ]
    )

choices = response.choices

for choice in choices:
    print(choice.message.content)