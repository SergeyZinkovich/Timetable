from builtins import len

import fdb
import tablesMetadata
import queryConstractor
from flask import Flask
from flask import request
from flask import render_template
from werkzeug.urls import url_encode
app = Flask(__name__)

def getTables(cur):
    sqlRequest = """SELECT a.RDB$RELATION_NAME
    FROM RDB$RELATIONS a
    WHERE RDB$SYSTEM_FLAG = 0 AND RDB$RELATION_TYPE = 0"""
    cur.execute(sqlRequest)
    tables = cur.fetchall()
    return [str(t[0]).strip() for t in tables]

def modifyUrl(**newValue):
    args = request.args.copy()

    for key, value in newValue.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))

def getConditionList():
    conditionList = ['LIKE', '>', '<', '>=', '<=', 'IN']
    return conditionList

def getElementsInPageNumbers():
    elementsInPageNumbers = ['10', '25', '50']
    return elementsInPageNumbers

@app.route("/")
def mainPage():
    global modifyUrl
    app.add_template_global(modifyUrl)
    selectedPage = int(request.args.get('page', 0))

    dataBase = fdb.connect(dsn='TIMETABLE.FDB', user='SYSDBA', password='masterkey', charset='UTF-8')
    cur = dataBase.cursor()

    tables = getTables(cur)
    selectedTable = request.args.get('tablesBox', '')
    if (selectedTable == '') or not (selectedTable in tables):
        selectedTable = tables[0]

    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
    queryBuilder = queryConstractor.queryBuilder()
    queryBuilder.createSelectWithJoin(meta, selectedTable)

    columns = queryBuilder.columnsSearchString.split(',')
    columnName = request.args.getlist('columnsBox')
    for i in range(len(columnName)):
        if (columnName[i] == '') or not (columnName[i] in columns):
            columnName[i] = columns[0]

    searchName = request.args.getlist('searchInput')
    conditions = getConditionList()
    selectedConditions = request.args.getlist('conditionsBox')
    for i in range(len(selectedConditions)):
        if selectedConditions[i] not in conditions:
            selectedConditions[i] = conditions[0]

    queryBuilder.addWhere(columnName, searchName, selectedConditions)

    sortOrder = request.args.get("sortOrderBox", '')
    if sortOrder not in columns:
        sortOrder = columns[0]
    queryBuilder.addSort(sortOrder)

    cur.execute(queryBuilder.query, searchName )
    sqlAns = cur.fetchall()

    columnsRealNames = [i.name for i in meta]

    elementsInPageNumbers = getElementsInPageNumbers()
    elementsInPage = request.args.get('elementsInPageBox', '')
    if elementsInPage == '' or int(elementsInPage) < 1:
        elementsInPage = 10
    elementsInPage = int(elementsInPage)
    pagesCount = len(sqlAns) // elementsInPage + 1

    return render_template("page.html", tables = tables, columns = columns, searchName = searchName,
                           selectedTable = selectedTable, selectedColumn = columnName,
                           elementsInPage = str(elementsInPage), elementsInPageNumbers = elementsInPageNumbers,
                           conditions = conditions, selectedConditions = selectedConditions,
                           columnsRealNames = columnsRealNames, sortOrder = sortOrder,
                           tableElements = sqlAns[selectedPage*elementsInPage:selectedPage*elementsInPage + elementsInPage],
                           pagesCount = pagesCount)

@app.route("/requestPage/<selectedTable>/<int:selectedId>/")
def requestPage(selectedTable = "WEEKDAYS", selectedId = 1):
    dataBase = fdb.connect(dsn='TIMETABLE.FDB', user='SYSDBA', password='masterkey', charset='UTF-8')
    cur = dataBase.cursor()
    queryBuilder = queryConstractor.queryBuilder()
    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.columnName for i in meta]
    columnsNames = columnsNames
    inputData = request.args.getlist('dataInput')
    if len(inputData) == 0:
        queryBuilder.createSelect(selectedTable, meta)
        queryBuilder.addWhere(["ID"], [selectedId], ["="])
        cur.execute(queryBuilder.query, [str(selectedId)])
        inputData = cur.fetchall()[0][1:]
    else:
        action = request.args.get('actionSelectBox', '')
        if action == "Удалить":
            queryBuilder.createDel(selectedTable, selectedId)
            cur.execute(queryBuilder.query)
        if action == "Изменить":
            queryBuilder.createUpdate(selectedTable, selectedId, columnsNames[1:])
            cur.execute(queryBuilder.query, inputData)
    return render_template("updateDeletePage.html", inputData = inputData, columnsNames = columnsNames)

@app.route('/create/<selectedTable>')
def createPage(selectedTable):
    dataBase = fdb.connect(dsn='TIMETABLE.FDB', user='SYSDBA', password='masterkey', charset='UTF-8')
    cur = dataBase.cursor()
    queryBuilder = queryConstractor.queryBuilder()
    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.columnName for i in meta]
    columnsNames = columnsNames
    inputData = request.args.getlist('dataInput')
    if len(inputData) !=0:
        queryBuilder.createInsert(selectedTable, columnsNames)
        cur.execute(queryBuilder.query, inputData)
    return render_template("createPage.html", columnsNames = columnsNames[1:])

if __name__ == "__main__":
    app.run()