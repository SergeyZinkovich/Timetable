import queryConstructor

queryBuilder = queryConstructor.queryBuilder()

class conflict:

    def __init__(self, id, name, sameFields):
        self.id = id
        self.name = name
        self.sameFields = sameFields

    def serchConflicts(self, cur):
        query = "SELECT ID, t1." + self.sameFields[0]
        for i in self.sameFields[1:]:
            query += ", t1." + i
        query += ''' FROM SCHED_ITEMS t1
                    WHERE exists (
                        SELECT * FROM SCHED_ITEMS t2 
                        WHERE t1.''' + self.sameFields[0] + ''' = t2.''' + self.sameFields[0]
        for i in self.sameFields[1:]:
            query += " AND t1." + i + " = t2." + i
        query += ''' AND t1.ID <> t2.ID
                    )\n'''
        query += "GROUP BY " + ",".join(self.sameFields) + ",ID"
        cur.execute(query)
        conflicts = cur.fetchall()
        k = 0
        for i in range(len(conflicts)):
            b = False
            if i > 0:
                for j in range(1, len(conflicts[i])):
                    if conflicts[i][j] != conflicts[i - 1][j]:
                        b = True
            if b == True:
                k += 1
            queryBuilder.createInsert("CONFLICTS", ["CONFLICT_ID", "CONFLICT_GROUP_ID", "ELEMENT_ID"])
            cur.execute(queryBuilder.query, [self.id, str(k), conflicts[i][0]])
            cur.transaction.commit()

class sameAudiens(conflict):
    def __init__(self):
        super().__init__("0", "Одинаковые аудитории", ["WEEKDAY_ID", "LESSON_ID", "AUDIENCE_ID"])

class sameTeacher(conflict):
    def __init__(self):
        super().__init__("1", "Разрыв преподавателя", ["WEEKDAY_ID", "LESSON_ID", "TEACHER_ID"])

class sameGroup(conflict):
    def __init__(self):
        super().__init__("2", "Разрыв группы", ["WEEKDAY_ID", "LESSON_ID", "GROUP_ID"])

def recreateConflictsTable(cur):
    cur.execute('''RECREATE TABLE CONFLICTS
                    (
                        ID Integer GENERATED BY DEFAULT AS IDENTITY,
                        CONFLICT_ID Integer NOT NULL,
                        CONFLICT_GROUP_ID Integer NOT NULL,
                        ELEMENT_ID Integer NOT NULL,
                        PRIMARY KEY (ID)
                    )''')
    cur.transaction.commit()

def createAllConflicts(cur):
    recreateConflictsTable(cur)
    sameAudiens().serchConflicts(cur)
    sameTeacher().serchConflicts(cur)
    sameGroup().serchConflicts(cur)