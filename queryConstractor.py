import tablesMetadata

class queryBuilder:
    query = ''
    columnsSearchString = ''

    def createSelect(self, tableName, meta):
        self.joinTable(meta, tableName)

    def joinTable(self, meta, tableName):
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

    def getQuery(self):
        return self.query