class Field:
    def __init__(self, columnName, name):
        self.columnName = columnName
        self.name = name
    def getColumns(self, tableName):
        return tableName + "." + self.columnName

class ReferenceField:
    def __init__(self, columnName, name, joinTableName, joinColumnName, selectColomnName):
        self.columnName = columnName
        self.name = name
        self.joinTableName = joinTableName
        self.joinColumnName = joinColumnName
        self.selectColomnName = selectColomnName
    def getColumns(self, tableName):
        return self.joinTableName + "." + self.selectColomnName

class TableMetadata:
    def __init__(self, tableRealName, tableName):
        self.tableRealName = tableRealName
        self.tableName = tableName

    def getMeta(self):
        return [val for val in self.__dict__.values() if isinstance(val, Field) or isinstance(val, ReferenceField)]

class audiences(TableMetadata):
    tableName = 'AUDIENCES'
    tableRealName = 'Аудитории'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Номер аудитории')


class lessons(TableMetadata):
    tableName = 'LESSONS'
    tableRealName = 'Занятия'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Название занятия')
    ORDER_NUMBER = Field('ORDER_NUMBER', 'Порядковый номер')


class groups(TableMetadata):
    tableName = 'GROUPS'
    tableRealName = 'Группы'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Номер группы')


class lesson_types(TableMetadata):
    tableName = 'LESSON_TYPES'
    tableRealName = 'Типы занятий'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Тип занятия')


class sched_items(TableMetadata):
    tableName = 'SCHED_ITEMS'
    tableRealName = 'Рассписание'
    ID = Field('ID', 'ID')
    LESSON_ID = ReferenceField('LESSON_ID', 'Номер пары', 'LESSONS', 'ID', 'Name')
    SUBJECT_ID = ReferenceField('SUBJECT_ID', 'Название предмета', 'SUBJECTS', 'ID', 'Name')
    AUDIENCE_ID = ReferenceField('AUDIENCE_ID', 'Номер аудитории', 'AUDIENCES', 'ID', 'Name')
    #GROUP_ID = ReferenceField('GROUP_ID', 'Номер группы', 'GROUPS', 'ID', 'Name')
    TEACHER_ID = ReferenceField('TEACHER_ID', 'Преподаватель', 'TEACHERS', 'ID', 'Name')
    TYPE_ID = ReferenceField('TYPE_ID', 'Тип занятия', 'LESSON_TYPES', 'ID', 'Name')
    WEEKDAY_ID = ReferenceField('WEEKDAY_ID', 'День недели', 'WEEKDAYS', 'ID', 'Name')


class subjects(TableMetadata):
    tableName = 'SUBJECTS'
    tableRealName = 'Предметы'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Название предмета')


class subject_group(TableMetadata):
    ID = Field('ID', 'ID')
    tableName = 'SUBJECT_GROUP'
    tableRealName = 'Предметы - Группы'
    SUBJECT_ID = ReferenceField('SUBJECT_ID', 'Название предмета', 'SUBJECTS', 'ID', 'Name')
    GROUP_ID = ReferenceField('GROUP_ID', 'Номер группы', 'GROUPS', 'ID', 'Name')


class subject_teacher(TableMetadata):
    ID = Field('ID', 'ID')
    tableName = 'SUBJECT_TEACHER'
    tableRealName = 'Предметы - Преподователи'
    SUBJECT_ID = ReferenceField('SUBJECT_ID', 'Название предмета', 'SUBJECTS', 'ID', 'Name')
    TEACHER_ID = ReferenceField('TEACHER_ID', 'Преподаватель', 'TEACHERS', 'ID', 'Name')


class teachers(TableMetadata):
    tableName = 'TEACHERS'
    tableRealName = 'Преподователи'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Преподаватель')


class weekdays(TableMetadata):
    tableName = 'WEEKDAYS'
    tableRealName = 'Дни недели'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'День недели')
    ORDER_NUMBER = Field('ORDER_NUMBER', 'Порядковый номер')

class log_status(TableMetadata):
    tableName = 'LOG_STATUS'
    tableRealName = 'Действия'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Действие')

class log(TableMetadata):
    tableName = 'LOG'
    tableRealName = 'Лог'
    ID = Field('ID', 'ID')
    TABLE_NAME = Field('TABLE_NAME', 'Таблица')
    STATUS = ReferenceField('STATUS', 'Действие', 'LOG_STATUS', 'ID', 'NAME')
    TABLE_PK = Field('TABLE_PK', 'TABLE_PK')
    CHANGE_TIME = Field('CHANGE_TIME', 'Время обновления')