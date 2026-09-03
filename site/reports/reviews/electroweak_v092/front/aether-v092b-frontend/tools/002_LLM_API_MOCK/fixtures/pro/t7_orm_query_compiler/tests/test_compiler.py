import unittest
from orm.models import Model, Field, ForeignKey
from orm.query import QuerySet, JoinCycleError
from orm.compiler import SQLCompiler

class Country(Model):
    id = Field(primary_key=True)
    name = Field()

class Organization(Model):
    id = Field(primary_key=True)
    country = ForeignKey(Country)

class User(Model):
    id = Field(primary_key=True)
    org = ForeignKey(Organization)
    status = Field()

class CyclicNode(Model):
    id = Field(primary_key=True)
    next_node = ForeignKey(lambda: CyclicNode)

class TestORMCompiler(unittest.TestCase):
    def test_basic_select_and_filter(self):
        qs = QuerySet(User).filter(status="active")
        sql, params = SQLCompiler(qs).compile()
        self.assertIn("SELECT", sql)
        self.assertIn("FROM users t0", sql)
        self.assertIn("t0.status = ?", sql)
        self.assertEqual(params, ["active"])

    def test_multi_table_join_traversal(self):
        qs = QuerySet(User).filter(org__country__name="Canada")
        sql, params = SQLCompiler(qs).compile()
        self.assertIn("JOIN organizations t1 ON t0.org_id = t1.id", sql)
        self.assertIn("JOIN countries t2 ON t1.country_id = t2.id", sql)
        self.assertIn("t2.name = ?", sql)
        self.assertEqual(params, ["Canada"])

    def test_duplicate_join_reuse(self):
        qs = QuerySet(User).filter(org__country__name="Canada", org__country__id=42)
        sql, params = SQLCompiler(qs).compile()
        # Must only join organizations and countries once each
        self.assertEqual(sql.count("JOIN organizations"), 1)
        self.assertEqual(sql.count("JOIN countries"), 1)
        self.assertEqual(len(params), 2)

if __name__ == "__main__":
    unittest.main()
