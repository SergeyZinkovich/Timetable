from builtins import len

import fdb
import tablesMetadata
import queryConstructor
from flask import Flask
from flask import request
from flask import render_template
from werkzeug.urls import url_encode

class searcher:
    table = []
    searchName = []
    selectedConditions = []
    selectedColumns = []

    def getConditionList(self):
        conditionList = ['LIKE', '>', '<', '>=', '<=', 'IN']
        return conditionList

    def search(self, queryBuilder):
        columns = queryBuilder.columnsSearchString.split(',')
        self.selectedColumns = request.args.getlist('columnsBox')
        for i in range(len(self.selectedColumns)):
            if (self.selectedColumns[i] == '') or not (self.selectedColumns[i] in columns):
                self.selectedColumns[i] = columns[0]

        self.searchName = request.args.getlist('searchInput')
        conditions = self.getConditionList()
        self.selectedConditions = request.args.getlist('conditionsBox')
        for i in range(len(self.selectedConditions)):
            if self.selectedConditions[i] not in conditions:
                self.selectedConditions[i] = conditions[0]

        queryBuilder.addWhere(self.selectedColumns, self.searchName, self.selectedConditions)

        sortOrder = request.args.get("sortOrderBox", '')
        if sortOrder not in columns:
            sortOrder = columns[0]
        queryBuilder.addSort(sortOrder)