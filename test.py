import json
import requests
import math

url = "https://api.thegraph.com/subgraphs/name/kybernetwork/kyberswap-elastic-matic"
res = []
time = 1662801537
while 1:
    query = "{swaps(limit: 1000, where: {pool_: {id: \"0x21c78a142b39d71686cb46b6320c5831e10b404c\"}, timestamp_gte: " + str(time) + "}, orderBy: timestamp){ transaction { id } amount0 amount1 timestamp } }"
    response = requests.post(url, json={'query': query})
    data = json.loads(response.text)
    swap = data['data']['swaps']
    # print(swap)
    if len(swap) == 0:
        break
    for d in swap:
        res.append(d)
        time = int(d['timestamp'])
    time += 1
    break

f = open("data.json", 'w')
json.dump(res, f, indent=4)

f.close()

