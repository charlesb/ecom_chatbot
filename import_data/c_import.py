import os, ssl, json, uuid
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to the SSL certificate file
SSL_CERTFILE = os.getenv("SSL_CERTFILE")

# List of past transactions

# Load products from the JSON file
with open('import_data/products.json', 'r') as f:
    products = json.load(f)

# Select some products for the past transactions
past_transactions = [product['sku'] for product in products[:4]]

auth_provider = PlainTextAuthProvider(os.getenv("CASSANDRA_USER"), os.getenv("CASSANDRA_PWD"))
ssl_options = {"ca_certs": SSL_CERTFILE, "cert_reqs": ssl.CERT_REQUIRED}
with Cluster(json.loads(os.getenv("CASSANDRA_CLUSTERS")), port=19748, ssl_options=ssl_options, auth_provider=auth_provider, load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='aiven')) as cluster:
        with cluster.connect() as session:
            # Here you can now read from or write to the database

            # Create a keyspace if it does not exist
            session.execute("""
            CREATE KEYSPACE IF NOT EXISTS customers 
            WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };
            """)

            # Use the keyspace
            session.execute("USE customers;")
            
            # Create customer_profiles table if it does not exist
            # session.execute("""
            # CREATE TABLE IF NOT EXISTS customer_profiles (
            #     user_id UUID PRIMARY KEY,
            #     name TEXT,
            #     email TEXT,
            #     past_transactions LIST<TEXT>
            # );
            # """)

            # Create conversations table if it does not exist
            session.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                user_id UUID,
                timestamp TIMESTAMP,
                message TEXT,
                response TEXT,
                PRIMARY KEY (user_id, timestamp)
            );
            """)

            # Insert a profile customer_profiles if it does not exist
            # session.execute("""
            # INSERT INTO customer_profiles (user_id, name, email, past_transactions)
            # VALUES (%s, %s, %s, %s) IF NOT EXISTS;
            # """, (uuid.uuid4(), 'Charles', 'charles@example.com', past_transactions))
