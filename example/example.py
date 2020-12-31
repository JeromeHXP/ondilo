from ondilo import Ondilo

client = Ondilo(redirect_uri="https://example.com/api")
print('Please go here and authorize,', client.get_authurl())

redirect_response = input('Paste the full redirect URL here:')
client.request_token(authorization_response=redirect_response)

print("Found all those pools: ", client.get_pools())