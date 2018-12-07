import boto3
import json
from boto3.dynamodb.conditions import Key


def createTableUrl(tableName): 
      
    keySchema=[
        {
            'AttributeName': 'url',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'message',
            'KeyType': 'RANGE'  #Sort key
        }
    ]
    attributeDefinitions=[
        {
            'AttributeName': 'url',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'message',
            'AttributeType': 'S'
        },

    ]
    provisionedThroughput={
        'ReadCapacityUnits': 25,
        'WriteCapacityUnits': 25
    }
        
    success = createTable(tableName, keySchema, attributeDefinitions, provisionedThroughput)


def putData(tableName, message):
    msg = json.loads(message)

    source = msg['source']
    sink = msg['sink']
    depth = msg['depth']
    
    putItemIfDoesNotExist(tableName, message, sink)
    

def createTable(tableName, keySchema, attributeDefinitions, provisionedThroughput):
    if not tableExists(tableName):
        print('table ' + tableName + ", created")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(TableName=tableName, KeySchema=keySchema, AttributeDefinitions=attributeDefinitions, ProvisionedThroughput=provisionedThroughput)
        return True
    return False
    
def putItemIfDoesNotExist(tableName, message, sink):
    if not itemExists(tableName, sink):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)
        response = table.put_item(TableName=tableName, Item={'message': message, 'url':sink})
        return response
    return -1
    
def getItem(tableName, url):
    if tableExists(tableName):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)
        fe = Key('url').eq(url)
        response = table.scan(FilterExpression=fe)
        for i in response['Items']:
            return i
        return -1
    
    
def getEverything(tableName):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.scan()
    return response
    
def getAllTableNames():
    dynamodb = boto3.client('dynamodb')
    response = dynamodb.list_tables()
    return response
    
def deleteTable(tableName):
    dynamodb = boto3.resource('dynamodb')
    if tableExists(tableName):
        table = dynamodb.Table(tableName)
        table.delete()
    
def deleteAllTables():
    tableNames = getAllTableNames()
    for tableName in tableNames['TableNames']:
        deleteTable(tableName)
    
def tableExists(tableName):
    response = getAllTableNames()
    for table in response['TableNames']:
        if (table == tableName):
            return True
    return False
    
def itemExists(tableName, url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    fe = Key('url').eq(url)
    response = table.scan(FilterExpression=fe)
  #  response = table.query(KeyConditionExpression=Key('url').eq(url))
    for i in response['Items']:
        return True
    return False