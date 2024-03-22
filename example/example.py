from ondilo import Ondilo

client = Ondilo(redirect_uri="https://example.com/api")
print('Please go here and authorize,', client.get_authurl())

redirect_response = input('Paste the full redirect URL here:')
client.request_token(authorization_response=redirect_response)

pools = client.get_pools()
print("Found all those pools: ", pools)

print(client.get_ICO_details(pools[0]['id']))
print(client.get_last_pool_measures(pools[0]['id']))
