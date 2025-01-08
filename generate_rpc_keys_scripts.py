import secrets

# Generate a secure random password
rpc_secret = secrets.token_urlsafe(32)
print(rpc_secret)