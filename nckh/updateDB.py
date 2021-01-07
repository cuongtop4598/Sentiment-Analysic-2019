import sqlite3
from sqlite3 import Error
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

def updateComment(connect,data):
    sql = "update nckh_comment set cment=?, stmAS=?, star=? where item_id=?"
    cur = connect.cursor()
    cur.execute(sql,data)
    connect.commit()
def updatePhone(connect,phoneid,data):
    sql = "update nckh_phone set name=?, rating=?, sold=?, price=?, imageURL=?, productURL=?, typeOF=?, store=?, sku=? where id=?"
    cur = connect.cursor()
    task = (data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[9],phoneid)
    cur.execute(sql, task)
    for cmt in data[8] :
        updateComment(connect,(cmt[0],STMALS.sentiment_analyse(cmt[0],3),cmt[1],phoneid))
    connect.commit()
def updateBrand(connect,data,cmts):
    sql = ''' INSERT INTO nckh_phone(name,rating,sold,price,imageURL,productURL,phone_id,typeOF,store,sku)
                VALUES(?,?,?,?,?,?,?,?,?,?) '''
    phoneid = insert_table(connect,data,sql)
    for cmt in cmts :
        cmtData = (cmt[0],STMALS.sentiment_analyse(cmt[0],3),cmt[1],phoneid)
    connect.commit()
