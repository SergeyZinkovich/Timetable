class Field:
    def __init__(self, columnName, name):
        self.columnName = columnName
        self.name = name

class ReferenceField:
    def __init__(self, columnName, name, joinTableName, joinColumnName, selectColomnName):
        self.columnName = columnName
        self.name = name
        self.joinTableName = joinTableName
        self.joinColumnName = joinColumnName
        self.selectColomnName = selectColomnName

class TableMetadata:
    def __init__(self, tableName):
        self.tableName = tableName

    def getMeta(self):
        return [val for attr, val in self.__dict__.items() if isinstance(val, Field) or isinstance(val, ReferenceField)]

class audiences(TableMetadata):
    tableName = 'Аудитории'
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Номер аудитории')


class lessons(TableMetadata):
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Название занятия')
    ORDER_NUMBER = Field('ORDER_NUMBER', 'Порядковый номер')


class groups(TableMetadata):
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Номер группы')


class lesson_types(TableMetadata):
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Тип занятия')


class sched_items(TableMetadata):
    ID = Field('ID', 'ID')
    LESSON_ID = ReferenceField('LESSON_ID', 'Номер пары', 'LESSONS', 'ID', 'Name')
    SUBJECT_ID = ReferenceField('SUBJECT_ID', 'Название предмета', 'SUBJECTS', 'ID', 'Name')
    AUDIENCE_ID = ReferenceField('AUDIENCE_ID', 'Номер аудитории', 'AUDIENCES', 'ID', 'Name')
    GROUP_ID = ReferenceField('GROUP_ID', 'Номер группы', 'GROUPS', 'ID', 'Name')
    TEACHER_ID = ReferenceField('TEACHER_ID', 'Преподаватель', 'TEACHERS', 'ID', 'Name')
    TYPE_ID = ReferenceField('TYPE_ID', 'Тип занятия', 'LESSON_TYPES', 'ID', 'Name')
    WEEKDAY_ID = ReferenceField('WEEKDAY_ID', 'День недели', 'WEEKDAYS', 'ID', 'Name')


class subjects(TableMetadata):
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Название предмета')


class subject_group(TableMetadata):
    SUBJECT_ID = ReferenceField('SUBJECT_ID', 'Название предмета', 'SUBJECTS', 'ID', 'Name')
    GROUP_ID = ReferenceField('GROUP_ID', 'Номер группы', 'GROUPS', 'ID', 'Name')


class subject_teacher(TableMetadata):
    SUBJECT_ID = ReferenceField('SUBJECT_ID', 'Название предмета', 'SUBJECTS', 'ID', 'Name')
    TEACHER_ID = ReferenceField('TEACHER_ID', 'Преподаватель', 'TEACHERS', 'ID', 'Name')


class teachers(TableMetadata):
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'Преподаватель')


class weekdays(TableMetadata):
    ID = Field('ID', 'ID')
    NAME = Field('NAME', 'День недели')
    ORDER_NUMBER = Field('ORDER_NUMBER', 'Порядковый номер')

