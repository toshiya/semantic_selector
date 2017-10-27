import unittest
from sqlalchemy import create_engine, func, sql
from semantic_selector import datasource
from sqlalchemy.orm import sessionmaker

class TestDatasource(unittest.TestCase):

    def test_read_canonical_topics(self):
        c = datasource.read_canonical_topics()
        self.assertEqual(len(c.keys()), 116)

    def test_inputs(self):
        engine = create_engine(
                'mysql+mysqlconnector://root:@localhost/register_form',
                echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        sub = session.query(datasource.Input.topic) \
                     .group_by(datasource.Input.topic) \
                     .having(func.count(1) > 10)
        r = session.query(datasource.Input) \
                   .filter(datasource.Input.topic.in_(sub)) \
                   .first()
        self.assertTrue(len(r.topic) > 2)
        self.assertTrue(r.topic != r.canonical_topic)

if __name__ == '__main__':
    unittest.main()
