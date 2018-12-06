import boto3
import calendar;
import time;
from boto3.dynamodb.conditions import Key

def createTableUrl(tableName): 
      
    keySchema=[
        {
            'AttributeName': 'url',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'id',
            'KeyType': 'RANGE'  #Sort key
        }
    ]
    attributeDefinitions=[
        {
            'AttributeName': 'url',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'id',
            'AttributeType': 'N'
        },

    ]
    provisionedThroughput={
        'ReadCapacityUnits': 25,
        'WriteCapacityUnits': 25
    }
        
    success = createTable(tableName, keySchema, attributeDefinitions, provisionedThroughput)


def createTable(tableName, keySchema, attributeDefinitions, provisionedThroughput):
    if not tableExists(tableName):
        print('table ' + tableName + ", created")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(TableName=tableName, KeySchema=keySchema, AttributeDefinitions=attributeDefinitions, ProvisionedThroughput=provisionedThroughput)
        return True
    return False
    
def putItemIfDoesNotExist(tableName, item):
    if not itemExists(tableName, item):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)
        timestamp = getTimestamp()
        response = table.put_item(TableName=tableName, Item={'url': item, 'id':timestamp})
        return response
    return -1
    
def getItem(tableName, url):
    if tableExists(tableName):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)
        response = table.get_item(Key={'url':url, 'id':0})
        return response
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
    
def getTimestamp():
    ts = calendar.timegm(time.gmtime())
    return ts
    
def tableExists(tableName):
    response = getAllTableNames()
    for table in response['TableNames']:
        if (table == tableName):
            return True
    return False
    
def itemExists(tableName, url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.query(KeyConditionExpression=Key('url').eq(url))
    for i in response['Items']:
        return True
    return False