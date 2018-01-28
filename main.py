from builtins import len

import optionsCreatHelper
import fdb
import tablesMetadata
import queryConstructor
import searchHelper
import conflictsModul
from flask import Flask
from flask import url_for
from flask import request
from flask import render_template
from werkzeug.urls import url_encode
app = Flask(__name__)

def getTables(cur):
    tables = ['SCHED_ITEMS', 'AUDIENCES', 'SUBJECT_GROUP', 'GROUPS',
              'LESSONS', 'LESSON_TYPES', 'SUBJECT_TEACHER', 'SUBJECTS', 'TEACHERS', 'WEEKDAYS', 'GROUPS']
    return tables

def getConflictsTypesNames():
    return ["Одинаковые аудитории", "Разрыв преподавателя", "Разрыв группы"]

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

dataBase = fdb.connect(dsn='TIMETABLE.FDB', user='SYSDBA', password='masterkey', charset='UTF-8')
cur = dataBase.cursor()
queryBuilder = queryConstructor.queryBuilder()

@app.route("/timeTable/")
def timeTablePage():
    metaClass = getattr(tablesMetadata, 'sched_items')
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.columnName for i in meta]
    columnsRealNames = [i.name for i in meta]
    queryBuilder.createSelectWithJoin(meta, 'sched_items')
    sercher = searchHelper.searcher()
    sercher.search(queryBuilder)
    tableElements = cur.execute(queryBuilder.query, sercher.searchName)
    tableElements = [list(i) for i in tableElements]

    selectedX = int(request.args.get('XBox', 0))
    if not selectedX in range(len(columnsNames)):
        selectedX = 0
    selectedY = int(request.args.get('YBox', 1))
    if not selectedY in range(len(columnsNames)):
        selectedY = 1

    showedColumns = request.args.getlist('showColumnsBox', int)
    if not showedColumns:
        showedColumns = columnsNames[:]
        showedColumns.pop(max(selectedX, selectedY))
        showedColumns.pop(min(selectedX, selectedY))

    tableDict = dict.fromkeys(i[selectedY] for i in tableElements)
    for i in tableDict:
        tableDict[i] = dict.fromkeys([j[selectedX] for j in tableElements])

    for i in tableElements:
        if tableDict[i[selectedY]][i[selectedX]] == None:
            tableDict[i[selectedY]][i[selectedX]] = [i]
        else:
            tableDict[i[selectedY]][i[selectedX]].append(i)

    showColumnsNames = request.args.get('showColumnsNamesCheckbox', 'true')

    return render_template("timeTable.html", columnsNames = columnsNames, showedColumns = showedColumns,
                           selectedX = columnsNames[selectedX], selectedY = columnsNames[selectedY],
                           tableElements = tableDict, showColumnsNames = showColumnsNames, columnsRealNames = columnsRealNames,
                           searchName = sercher.searchName, selectedConditions = sercher.selectedConditions, conditions = getConditionList(),
                           selectedColumn = sercher.selectedColumns)

@app.route("/")
@app.route("/<selectedTable>/")
def mainPage(selectedTable = "WEEKDAYS"):
    global modifyUrl
    global prevTable
    app.add_template_global(modifyUrl)
    selectedPage = int(request.args.get('page', 0, int))

    tables = getTables(cur)
    if (selectedTable == '') or not (selectedTable in tables):
        selectedTable = tables[0]

    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
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

    cur.execute(queryBuilder.query, queryBuilder.args )
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

#пользовательское изменение/удаление
@app.route("/updateDelete/<selectedTable>/<int:selectedId>/")
def updateDeletePage(selectedTable = "WEEKDAYS", selectedId = 1):
    commited = 0
    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.columnName for i in meta]
    inputData = request.args.getlist('dataInput')

    optionsCreator = optionsCreatHelper.optionsCreator(meta, cur)

    if len(inputData) == 0:
        queryBuilder.createSelect(selectedTable, meta)
        queryBuilder.addWhere(["ID"], [selectedId], ["="])
        cur.execute(queryBuilder.query, [str(selectedId)])
        inputData = cur.fetchall()[0][1:]
        inputData = list(inputData)
    if len(inputData) != 0:
        action = request.args.get('actionSelectBox', '')
        if action == "Удалить":
            queryBuilder.createDel(selectedTable, selectedId)
            cur.execute(queryBuilder.query, [str(selectedId)])
            commited = 1
        if action == "Изменить":
            queryBuilder.createUpdate(selectedTable, selectedId, columnsNames)
            inputData.append(str(selectedId))
            cur.execute(queryBuilder.query, [i if i != "None" else None for i in inputData])
            commited = 1
        cur.transaction.commit()
    return render_template("updateDeletePage.html", inputData = inputData, columnsNames = columnsNames[1:],
                           commited = commited, options = optionsCreator.pikerOptionsDict)

#программное изменение
@app.route("/updateDelete/<selectedTable>/<int:selectedId>/<x>/<xValue>/<y>/<yValue>/")
def programUpdate(selectedTable = "WEEKDAYS", selectedId = 1, x = '', xValue = '', y = '', yValue = ''):
    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.columnName for i in meta]

    optionsCreator = optionsCreatHelper.optionsCreator(meta, cur)

    queryBuilder.createSelect(selectedTable, meta)
    queryBuilder.addWhere(["ID"], [selectedId], ["="])
    cur.execute(queryBuilder.query, [str(selectedId)])
    inputData = cur.fetchall()[0][1:]
    inputData = list(inputData)
    if ((x == "ID") and (xValue != str(inputData[0]))) or ((y == "ID") and (yValue != str(inputData[0]))):
        return
    for i in range(1, len(columnsNames)):
        if columnsNames[i] == x:
            inputData[i - 1] = optionsCreator.pikerOptionsDictBack[x][xValue]
        if columnsNames[i] == y:
            inputData[i - 1] = optionsCreator.pikerOptionsDictBack[y][yValue]
    queryBuilder.createUpdate(selectedTable, selectedId, columnsNames)
    inputData.append(str(selectedId))
    cur.execute(queryBuilder.query, [i if i != "None" else None for i in inputData])
    cur.transaction.commit()
    return "succes"

@app.route("/create/<selectedTable>")
@app.route("/create/<selectedTable>/<x>/<xValue>/<y>/<yValue>/")
def createPage(selectedTable, x = '', xValue = '', y = '', yValue = ''):
    commited = 0
    metaClass = getattr(tablesMetadata, selectedTable.lower())
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.columnName for i in meta]
    inputData = request.args.getlist('dataInput')

    optionsCreator = optionsCreatHelper.optionsCreator(meta, cur)

    if len(inputData) !=0:
        queryBuilder.createInsert(selectedTable, columnsNames[1:])
        cur.execute(queryBuilder.query, [i if i != "None" else None for i in inputData])
        cur.transaction.commit()
        commited = 1
    if len(inputData) == 0:
        for i in range(1, len(columnsNames) - 1):
            if columnsNames[i] == x:
                inputData[i - 1] = optionsCreator.pikerOptionsDictBack[x][xValue]
            elif columnsNames[i] == y:
                inputData[i - 1] = optionsCreator.pikerOptionsDictBack[y][yValue]
            else:
                inputData.append('')
    return render_template("createPage.html", columnsNames = columnsNames[1:],
                           inputData = inputData, commited = commited, options = optionsCreator.pikerOptionsDict)

@app.route("/conflicts/<int:conflictId>")
@app.route("/conflicts")
def conflictsPage(conflictId = 0):
    if not conflictId in range(3):
        conflictId = 0
    conflictsModul.createAllConflicts(cur)
    metaClass = getattr(tablesMetadata, 'sched_items')
    meta = metaClass.getMeta(metaClass)
    columnsNames = [i.name for i in meta]
    queryBuilder.getConflicts(conflictId, meta)
    cur.execute(queryBuilder.query)
    sqlAns = cur.fetchall()

    return render_template("conflictsPage.html", conflictsTypesNames = getConflictsTypesNames(),
                           conflictId = conflictId, columnsNames = columnsNames, tableElements = sqlAns )

if __name__ == "__main__":
    app.run()