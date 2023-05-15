import json
import requests
import math
import threading

b = {}
def block_by_time(time):
    url = "https://api.thegraph.com/subgraphs/name/kybernetwork/polygon-blocks"
    query = "{ blocks(where: {timestamp_gte: " + str(time) + "}, first: 1, orderBy: timestamp, orderDirection: asc) { timestamp number } }"
    response = requests.post(url, json={'query': query})
    data = json.loads(response.text)
    return int(data['data']['blocks'][0]['number'])

def first_time(poolid):
    url = "https://api.thegraph.com/subgraphs/name/kybernetwork/kyberswap-elastic-matic"
    query = "{pools(where: {id: \"" + poolid + "\"}) { createdAtBlockNumber } }"
    response = requests.post(url, json={'query': query})
    data = json.loads(response.text)
    return int(data['data']['pools'][0]['createdAtBlockNumber'])

def get_data_pool_at_block(block, poolid):
    url = "https://api.thegraph.com/subgraphs/name/kybernetwork/kyberswap-elastic-matic"
    query = "{ pools(block: {number: " + str(block) + "}, where: {id: \"" + poolid + "\"}){ reinvestL reinvestLLast sqrtPrice totalSupply } }"
    response = requests.post(url, json={'query': query})
    data = json.loads(response.text)
    data['data']['pools'][0]['reinvestL'] = int(data['data']['pools'][0]['reinvestL'])
    data['data']['pools'][0]['reinvestLLast'] = int(data['data']['pools'][0]['reinvestLLast'])
    data['data']['pools'][0]['sqrtPrice'] = int(data['data']['pools'][0]['sqrtPrice'])
    data['data']['pools'][0]['totalSupply'] = int(data['data']['pools'][0]['totalSupply'])
    b[str(block)] = data['data']['pools'][0]
    return data['data']['pools'][0]

def get_swaps_of_pool(poolid):
    url = "https://api.thegraph.com/subgraphs/name/kybernetwork/kyberswap-elastic-matic"
    res = []
    time = 1640995200 #2022-01-01 07:00
    while 1==1:
        query = "{swaps(limit: 1000, where: {pool_: {id: \"" + poolid + "\"}, timestamp_gte: " + str(time) + "}, orderBy: timestamp){ timestamp } }"
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
    return res

burn = open("polygon.json")
rburns = json.load(burn)

def get_tx_burnR_by_poolid_and_block(block, poolid):
    res = []
    for rburn in rburns:
        if rburn['pool_address'] == poolid and rburn['block_number'] == block:
            res.append(rburn)
    return res

f = open("pool_polygon.json")
pools = json.load(f)
fee = []
for pool in pools:
    swaps = get_swaps_of_pool(pool['id'])
    blocks = []
    for swap in swaps:
        block = block_by_time(swap['timestamp'])
        blocks.append(block)
    dmm = 0
    rcurve = 0
    b = {}
    threads = []
    for block in blocks: 
        t = threading.Thread(target=get_data_pool_at_block, args=(block, pool['id']))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
        
    for block in blocks:
        qty0_pre = b[str(block-1)]['reinvestLLast'] / b[str(block-1)]['sqrtPrice']
        qty1_pre = b[str(block-1)]['reinvestLLast'] * b[str(block-1)]['sqrtPrice']
        LperT_pre = b[str(block-1)]['reinvestLLast'] / b[str(block-1)]['totalSupply']
        
        rburns = get_tx_burnR_by_poolid_and_block(block, pool['id'])
        qty0 = 0
        qty1 = 0
        rtoken = 0
        for rburn in rburns:
            rtoken += rburn['qty']
            qty0 += rburn['qty0']
            qty1 += rburn['qty1']
            
        
        qty0 += (b[str(block)]['reinvestLLast'] / b[str(block)]['sqrtPrice'])
        qty1 += (b[str(block)]['reinvestLLast'] * b[str(block)]['sqrtPrice'])
        reinvestL = math.sqrt(qty0 * qty1)
        totalSupply = b[str(block)]['totalSupply'] + rtoken
        LperT = reinvestL / totalSupply
        
        dmm += (totalSupply - b[str(block-1)]['totalSupply']) * LperT
        rcurve += b[str(block-1)]['totalSupply'] * (LperT - LperT_pre)
        
    fee.append({"pool": pool['id'], "dmm": dmm, "rcurve": rcurve})
    break

ff = open("polygon_fee.json", 'w')
json.dump(fee, ff, indent=4)

ff.close()
        