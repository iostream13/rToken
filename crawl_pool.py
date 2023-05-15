import requests
import json

url = "https://api.thegraph.com/subgraphs/name/kybernetwork/kyberswap-elastic-optimism"

query = "{ pools(first: 1000) { id token0 { id symbol decimals } token1 { id symbol decimals } } }"
response = requests.post(url, json={'query': query})

f = open("pool_optimism.json", 'w')

data = json.loads(response.text)

json.dump(data, f, indent=4)

f.close()
