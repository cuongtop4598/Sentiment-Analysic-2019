import sqlite3
from sqlite3 import Error
import json
from sentimentAnalysis import STMALS
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn
 
 
def insert_table(conn, project,sql):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    
    cur = conn.cursor()
    cur.execute(sql, project)
    return cur.lastrowid 

# get data from file
def readFile(file_name):
    f = open(file_name,"r",encoding='utf-8')
    data = json.load(f)
    return data


def main():
    
    names = ["Apple","Samsung","Xiaomi" ,"Vivo","Realme","Oppo","Wiko","Vsmart","Neffos","Nokia","BlackBerry","Bluboo","Brown","Honor"
    ,"Huawei","Infinix","Itel","JBL","Masstel","Mobell","Oukitel","Suntek"]
    database = "./db.sqlite3"
    
    conn = create_connection(database)
    sqlPhone = ''' INSERT INTO nckh_brand(trademark,amount,url)
                VALUES(?,?,?) '''
    sqlItem = ''' INSERT INTO nckh_phone(name,rating,sold,price,imageURL,productURL,brand_id,typeOF,store,sku)
                VALUES(?,?,?,?,?,?,?,?,?,?) '''
    sqlComments = ''' INSERT INTO nckh_comment(cment,stmAS,star,phone_id) 
                VALUES(?,?,?,?) '''
    with conn:
        for x in names :
            file_name = "media/assets/%s.crash" % x
            data = readFile(file_name)
            # create a database connection
            #create a new project
            for x in data['Phone']:
                Phone = (x['trademark'],x['amount'],x['URL'])
                Phoneid = insert_table(conn,Phone,sqlPhone)
                for y in x['Items']['items']:
                    Item = (y['name'], float(y['rating']), int(y['comment']),int(y['price']),y['imageURL'],y['productURL'],Phoneid,y['type'],y['store'],y['sku'])
                    Itemid = insert_table(conn, Item,sqlItem)
                    l = len(y['cmts'])
                    for i in range(l) :
                        CmtData = (y["cmts"][i][0],STMALS.sentiment_analyse(y["cmts"][i][0],3),y['cmts'][i][1],Itemid)
                        print(CmtData)
                        Cmtsid = insert_table(conn,CmtData,sqlComments)
                        print(Cmtsid)
    conn.close()
 
 
if __name__ == '__main__':
    main()