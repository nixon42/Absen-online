import os
import sqlite3

# import var

path = os.path.join(os.path.abspath('.'), 'app_db.db')

conn = sqlite3.connect(path, check_same_thread=False)
cursor = conn.cursor()


def addUser(teleId, chatId):
    sql = f"""
    INSERT INTO user_tb (teleId, chatId, url, waktu, libur) VALUES ({teleId}, {chatId}, 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSfxLBNunvllYNwTcb9InUTl9lGYogjJrLJ8QHqmHiRngEfxSA/formResponse', '06.00', '[Sat:Sun]');
    """
    cursor.execute(sql)
    conn.commit()


def addConfig(id, col, val):
    sql = f"""
    UPDATE user_tb SET {col} = "{val}" WHERE teleId LIKE "{id}";
    """
    # print(sql)
    cursor.execute(sql)
    conn.commit()


def get(id, col, like='teleId'):
    sql = f"""
    SELECT {col} FROM 'user_tb' WHERE {like} LIKE "{id}";
    """
    # print(sql)
    row = cursor.execute(sql)
    data = row.fetchall()[0]
    data = 'Kosong !' if data.__contains__(None) else data[0]
    return data


def check(id):
    sql = f"""
    SELECT url,payload,waktu,libur FROM user_tb WHERE teleId LIKE {id};
    """
    row = cursor.execute(sql)
    data = row.fetchone()
    # print(data)
    if data != None:
        return True
    return False


def getData(id):
    sql = f"""
    SELECT * FROM user_tb WHERE teleId LIKE "{id}";
    """
    row = cursor.execute(sql)
    col = list(map(lambda x: x[0], row.description))
    data = row.fetchall()[0]
    data = list(data)
    dataDict = dict(zip(col, data))
    return dataDict


def checkTrig():
    sql = """
    SELECT teleId,trigger FROM user_tb;
    """
    row = cursor.execute(sql)
    data = row.fetchall()
    # id = list(map(lambda x : x[0], ))
    trig = {}
    for x in data:
        if x[1] != None and x[1] != '':
            trig[x[1]] = x[0]
    return trig
