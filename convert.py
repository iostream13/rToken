import csv 
import json 

def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        f = open("pool_polygon.json")
        pools = json.load(f)
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            str = row['block_number']
            str = str[:-4]
            number = float(str)
            row['block_number'] = int(number * 1e7)
            row['qty'] = int(row['qty'])
            row['qty0'] = int(row['qty0'])
            row['qty1'] = int(row['qty1'])
            for pool in pools:
                if pool["id"] == row['pool_address']:
                    row["token0"] = pool["token0"]["symbol"]
                    row["decimals0"] = int(pool["token0"]["decimals"])
                    row["token1"] = pool["token1"]["symbol"]
                    row["decimals1"] = int(pool["token1"]["decimals"])
                    break
                
            #add this python dict to json array
            jsonArray.append(row)
  
    #convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)
          
csvFilePath = r'polygon.csv'
jsonFilePath = r'polygon.json'
csv_to_json(csvFilePath, jsonFilePath)