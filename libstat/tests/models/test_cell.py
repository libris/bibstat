# -*- coding: UTF-8 -*-
from libstat.models import Cell
from libstat.tests import MongoTestCase


class CellTest(MongoTestCase):

    def test_caches_variable_when_first_fetched(self):
        variable = self._dummy_variable()
        cell = Cell(variable_key=variable.key)

        self.assertEquals(cell._variable, None)
        self.assertEquals(cell.variable, variable)
        self.assertEquals(cell._variable, variable)

        variable2 = self._dummy_variable()
        cell.variable_key = variable2.key

        self.assertEquals(cell.variable, variable)
        self.assertEquals(cell._variable, variable)