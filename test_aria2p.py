from aria2p import API, Client

# Connect to the aria2c instance
client = Client(host="http://localhost", port=6800, secret="APZbUnwVUUVtYiTnZ7KNmMfdtjVEw4M540RuHs7Lm5E")
api = API(client)

# Get aria2c version
version_info = client.get_version()
print(f"aria2 version: {version_info['version']}")
