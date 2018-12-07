from dynamoIterface import *
import time
import json
tableName = "Urls"
url = 'https://www.test.de/kontakt/'

# I guess the master would create the table, this can take around 10 sec, so some assurance has to be made that it exists when the crawler starts
createTableUrl(tableName)
print("Table is being created, please wait...")
time.sleep(2)

response = tableExists(tableName)
print("Table " + tableName + " exists?: " + str(response))

# if other information has to be stored, simply add it to the message object, just make sure you are aware of it when retrieving objects
message = json.dumps({'source':'https://test.de', 'sink':'https://www.test.de/kontakt/', 'depth': 3})

# the worker probably only cares about the command as it checks if an item with the url exists and only puts it if it does not exist yet
putData(tableName, message)
print("PUT: " + str(response))

# gets only one item defined by its url
item = getItem(tableName, url)
if (item != -1):
    jsonObj = json.loads(str(item['message']))
    print(jsonObj['source'])
    print(jsonObj['sink'])
    print(jsonObj['depth'])

    
# checks if if item exists or not
response = itemExists(tableName, url)
print (response)

# return all items in the table, this would be for the master to draw the graph, let me know if you not something differnt
scan = getEverything(tableName)
for i in scan['Items']:
    jsonObj = json.loads(str(item['message']))
    print(jsonObj['source'])
    print(jsonObj['sink'])
    print(jsonObj['depth'])
    
# to delte the table
#deleteTable(tableName)
