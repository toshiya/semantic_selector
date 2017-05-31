# -*- coding: utf-8 -*-
import os
import mysql.connector


class InputTabs(object):
    class __InputTabs:
        def __init__(self):
            self.conn = mysql.connector.connect(
                            user='root',
                            password='',
                            host='localhost',
                            database='login_form')

        def fetch_all(self, table_name):
            cursor = self.conn.cursor(dictionary=True)
            stmt = "SELECT * FROM " + table_name
            cursor.execute(stmt)
            records = cursor.fetchall()
            return records

    instance = None

    def __init__(self):
        if not InputTabs.instance:
            InputTabs.instance = InputTabs.__InputTabs()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def cleanup():
        InputTabs.instance.conn.close()
        InputTabs.instance = None


if __name__ == "__main__":
    print("datasource")
