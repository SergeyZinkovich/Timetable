from builtins import len

import fdb
from flask import Flask
from flask import request
from flask import render_template
app = Flask(__name__)

def getTables(cur):
    sqlRequest = """SELECT a.RDB$RELATION_NAME
    FROM RDB$RELATIONS a
    WHERE RDB$SYSTEM_FLAG = 0 AND RDB$RELATION_TYPE = 0"""
    cur.execute(sqlRequest)
    tables = cur.fetchall()
    return [str(tables[i])[2:-3].strip() for i in range(len(tables))]

def getColums(cur, tableName):
    sqlRequest = """select rdb$field_name 
    from rdb$relation_fields
    where rdb$relation_name= \'""" + tableName + "\'"
    cur.execute(sqlRequest)
    columns = cur.fetchall()
    return [str(columns[i])[2:-3].strip() for i in range(len(columns))]

@app.route("/")
def mainPage():
    dataBase = fdb.connect(dsn='TIMETABLE.FDB', user='SYSDBA', password='masterkey', charset='UTF8')
    cur = dataBase.cursor()
    tables = getTables(cur)
    tableName = request.args.get('tablesBox', '')
    if tableName == '':
        tableName = tables[0]
    columns = getColums(cur, tableName)
    columnName = request.args.get('columnsBox', '')
    if columnName == '':
        columnName = columns[0]
    searchName = request.args.get('searchInput', '')

    sqlRequest = "select * from " + tableName
    if len(searchName) != 0:
        sqlRequest += " where " + columnName + " like \'" + searchName + "\'"
    cur.execute(sqlRequest)
    sqlAns = cur.fetchall()

    tableElements = [[] for i in range(len(sqlAns))]
    for i in range(len(sqlAns)):
        tableElements[i] = str(sqlAns[i])[1:-1].split(',')
    return render_template("page.html", tables = tables, columns = columns, selectedTable = tableName,
                           selectedColumn = columnName, tableElements = tableElements)

if __name__ == "__main__":
    app.run()