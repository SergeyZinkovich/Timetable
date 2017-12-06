import tablesMetadata

class queryBuilder:
    query = ''
    columnsSearchString = ''

    def createSelect(self, tableName, meta):
        self.columnsSearchString = ','.join(i.columnName for i in meta)
        self.query = "select " + self.columnsSearchString + " from " + tableName + " "

    def createSelectWithJoin(self, meta, tableName):
        self.columnsSearchString = ','.join(i.getColumns(tableName) for i in meta)
        self.query = "select " + self.columnsSearchString +" from " + tableName + " "
        # self.joins = ''.join(i.getJoin for i in meta)
        for i in meta:
            if isinstance(i, tablesMetadata.ReferenceField):
                self.query += "left join " + i.joinTableName + " on " + \
                              tableName + "." + i.columnName + " = " + i.joinTableName + "." + i.joinColumnName + "\n"

    def addWhere(self, columnName, searchName, selectedConditions):
        k = 0
        for i in range(len(searchName)):
            if k == 0:
                self.query += " where " + columnName[i] + " " + selectedConditions[i] +" ? "
                k += 1
            else:
                self.query += " and " + columnName[i] + " " + selectedConditions[i] +" ? "

    def addSort(self, sortOrder):
        self.query += "order by " + sortOrder

    def createInsert(self, tableName, columnsNames):
        self.query = "insert into " + tableName + " "
        self.query += "(" + ",".join(i for i in columnsNames) + ")\n"
        self.query += "values (" + "none" + ",?" * (len(columnsNames) - 1)+")"

    def createUpdate(self, tableName, id, columnsNames):
        self.query = "update " + tableName + "\n"
        for i in range(1, len(columnsNames)):
            self.query += "set " + columnsNames[i] + "= ?\n"
        self.query += " where ID = " + str(id)

    def createDel(self, tableName, id):
        self.query = "delete from " + tableName + " where ID = " + str(id)

    def getQuery(self):
        return self.query