from builtins import len

import fdb
import tablesMetadata
import queryConstractor
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
    return [str(t[0]).strip() for t in tables]

def getColums(cur, tableName):
    sqlRequest = """select rdb$field_name 
    from rdb$relation_fields
    where rdb$relation_name= \'""" + tableName + "\'"
    cur.execute(sqlRequest)
    columns = cur.fetchall()
    return [str(c[0]).strip() for c in columns]

@app.route("/")
def mainPage():
    dataBase = fdb.connect(dsn='TIMETABLE.FDB', user='SYSDBA', password='masterkey', charset='UTF8')
    cur = dataBase.cursor()
    tables = getTables(cur)

    tableName = request.args.get('tablesBox', '')
    if (tableName == '') or not (tableName in tables):
        tableName = tables[0]
    metaClass = getattr(tablesMetadata, tableName.lower())
    meta = metaClass.getMeta(metaClass)
    #columns = getColums(cur, tableName)
    columns = [i.name for i in meta]
    columnName = request.args.get('columnsBox', '')
    if (columnName == '') or not (columnName in columns):
        columnName = columns[0]
    searchName = request.args.get('searchInput', '')

    queryBuilder = queryConstractor.queryBuilder(tableName, columnName, searchName, meta)
    cur.execute(queryBuilder.query, (searchName, ))
    sqlAns = cur.fetchall()

    tableElements = [[] for i in range(len(sqlAns) + 1)]
    tableElements[0] = columns
    for i in range(len(sqlAns)):
        tableElements[i + 1] = [j for j in sqlAns[i]]
    return render_template("page.html", tables = tables, columns = columns, selectedTable = tableName,
                           selectedColumn = columnName, tableElements = tableElements)

if __name__ == "__main__":
    app.run()