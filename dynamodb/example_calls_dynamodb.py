from dynamoIterface import *
import time

tableName = "Urls"
url = 'https://www.test.de'

# I guess the master would create the table, this can take around 10 sec, so some assurance has to be made that it exists when the crawler starts
createTableUrl(tableName)
print("Table is being created, please wait...")
time.sleep(20)

response = tableExists(tableName)
print("Table " + tableName + " exists?: " + str(response))


# the worker probably only cares about the command as it checks if an item with the url exists and only puts it if it does not exist yet
response = putItemIfDoesNotExist(tableName, url)
print("PUT: " + str(response))

# gets only one item defined by its url
item = getItem(tableName, url)
if (item != -1):
    print("GET: " + str(item))
    
# checks if if item exists or not
response = itemExists(tableName, url)
print (response)

# return all items in the table, this would be for the master to draw the graph, let me know if you not something differnt
scan = getEverything(tableName)
for i in scan['Items']:
    print(str(i))
