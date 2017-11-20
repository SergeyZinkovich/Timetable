import tablesMetadata

class queryBuilder:
    query = ''

    def __init__(self, tableName, columnName, searchName, meta):
        self.createQuery(tableName, columnName, searchName)
        self.joinTable(meta, tableName)

    def createQuery(self, tableName, columnName, searchName):
        self.query = "select %s from " + tableName
        if len(searchName) != 0:
            self.query += " where " + columnName + " = ?"
        return self.query

    def joinTable(self, meta, tableName):
        columnsString = ','.join(tableName + "." + i.columnName for i in meta)
        for i in meta:
            if isinstance(i, tablesMetadata.ReferenceField):
                self.query += " left join " + i.joinTableName + " on " + \
                              tableName + "." + i.columnName + " = " + i.joinTableName + "." + i.joinColumnName + "\n"
                columnsString = columnsString.replace(tableName + "." + i.columnName, i.joinTableName + '.' + i.selectColomnName, 1)
        self.query = self.query % columnsString
        return self.query

    def getQuery(self):
        return self.query