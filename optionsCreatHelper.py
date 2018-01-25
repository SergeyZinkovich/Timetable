import tablesMetadata
class optionsCreator:
    pikerOptionsDict = {}
    pikerOptionsDictBack = {}

    def __init__(self, meta, cur):
        pikerOptionsDict = {}
        pikerOptionsDictBack = {}
        for i in meta:
            if isinstance(i, tablesMetadata.ReferenceField):
                q = 'Select %s, %s from %s ' % (i.selectColomnName, i.joinColumnName, i.joinTableName)
                cur.execute(q)
                a = cur.fetchall()
                self.pikerOptionsDict[i.columnName] = {i[1]: i[0] for i in a}
                self.pikerOptionsDict[i.columnName][None] = 'None'
                self.pikerOptionsDictBack[i.columnName] = dict(a)
                self.pikerOptionsDictBack[i.columnName]['None'] = None
            else:
                self.pikerOptionsDict[i.columnName] = ''
                self.pikerOptionsDictBack[i.columnName] = ''