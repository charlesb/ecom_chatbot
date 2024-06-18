import os, ssl, json
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to the SSL certificate file
SSL_CERTFILE = os.getenv("SSL_CERTFILE")

auth_provider = PlainTextAuthProvider(os.getenv("CASSANDRA_USER"), os.getenv("CASSANDRA_PWD"))
ssl_options = {"ca_certs": SSL_CERTFILE, "cert_reqs": ssl.CERT_REQUIRED}
with Cluster(json.loads(os.getenv("CASSANDRA_CLUSTERS")), port=19748, ssl_options=ssl_options, auth_provider=auth_provider, load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='aiven')) as cluster:
        with cluster.connect() as session:
            # Here you can now read from or write to the database
            # List all keyspaces
            print(session.execute("SELECT * FROM system_schema.keyspaces"))
