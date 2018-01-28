import tablesMetadata

class queryBuilder:
    query = ''
    columnsSearchString = ''
    args = []

    def createSelect(self, tableName, meta):
        self.columnsSearchString = ','.join(i.columnName for i in meta)
        self.query = "select " + self.columnsSearchString + " from " + tableName + " "

    def createSelectWithJoin(self, meta, tableName):
        self.columnsSearchString = ','.join(i.getColumns(tableName) for i in meta)
        self.query = "select " + self.columnsSearchString +" from " + tableName + " "
        # self.joins = ''.join(i.getJoin for i in meta)
        self.addJoins(tableName, meta)

    def addJoins(self, tableName, meta):
        for i in meta:
            if isinstance(i, tablesMetadata.ReferenceField):
                self.query += "left join " + i.joinTableName + " on " + \
                              tableName + "." + i.columnName + " = " + i.joinTableName + "." + i.joinColumnName + "\n"

    def addWhere(self, columnName, searchName, selectedConditions):
        k = 0
        self.args = searchName[:]
        for i in range(len(searchName)):
            if k == 0:
                self.query += " where " + columnName[i] + " " + selectedConditions[i] + " ? "
                k += 1
            else:
                self.query += " and " + columnName[i] + " " + selectedConditions[i] + " ? "
            if selectedConditions[i] == "LIKE":
                self.args[i] = '%' + self.args[i] + '%'

    def addSort(self, sortOrder):
        self.query += "order by " + sortOrder

    def createInsert(self, tableName, columnsNames):
        self.query = "insert into " + tableName + " "
        self.query += "(" + ",".join(i for i in columnsNames) + ")\n"
        self.query += "values (" + "?" + ",?" * (len(columnsNames) - 1)+")"

    def createUpdate(self, tableName, id, columnsNames):
        self.query = "update " + tableName + "\n"
        for i in range(1, len(columnsNames)):
            if i == 1:
                self.query += "set " + columnsNames[i] + "= ?\n"
            else:
                self.query += ',' + columnsNames[i] + "= ?\n"
        self.query += " where ID = ?"

    def createDel(self, tableName, id):
        self.query = "delete from " + tableName + " where ID = ?"

    def getConflicts(self, conflictId, meta):
        self.query = '''Select c.CONFLICT_GROUP_ID, ''' + ','.join(i.getColumns("SCHED_ITEMS") for i in meta) + '''  from CONFLICTS c 
                        inner join SCHED_ITEMS on c.ELEMENT_ID = SCHED_ITEMS.ID\n'''
        self.addJoins("SCHED_ITEMS", meta)
        self.addConflictsWhere(conflictId)

    def addConflictsWhere(self, conflictId):
        self.query +=  "where c.CONFLICT_ID = " + str(conflictId)