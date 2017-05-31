# -*- coding: utf-8 -*-
import os
import mysql.connector
import MeCab

_MECAB_TOKENIZER = MeCab.Tagger("-Owakati")
# Work Around for mecab-python3 bug
# https://shogo82148.github.io/blog/2015/12/20/mecab-in-python3-final/
_MECAB_TOKENIZER.parse('')

def fetch_all(table_name):
    db_password = 'root'
    if 'DB_PASSWORD' in os.environ:
        db_password = os.environ['DB_PASSWORD']
    conn = mysql.connector.connect(
            user='root',
            password=db_password,
            host='localhost',
            database='login_form'
            )
    cursor = conn.cursor(dictionary=True)
    stmt = "SELECT * FROM " + table_name
    cursor.execute(stmt)
    records = cursor.fetchall()
    conn.close()
    return records


if __name__ == "__main__":
    print("preprocessor")
