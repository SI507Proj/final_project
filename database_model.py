import sys

import psycopg2
import psycopg2.extras
from psycopg2 import sql

from db_config import *

class DBManager(object):
    REGION_TABLE = "Region"
    VIDEO_TABLE = "Video"

    def __init__(self):
        (self.db_conn, self.db_cur) = self.__get_connection_and_cursor()
        self.__setup_database()

    # setup connection and cursor
    def __get_connection_and_cursor(self):
        try:
            if db_password != "":
                db_conn = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
                print("Success connecting to database")
            else:
                db_conn = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
        except:
            print("Unable to connect to the database. Check server and credentials.")
            sys.exit(1) # Stop running program if there's no db connection.

        db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        return db_conn, db_cur

    # create Region and Video database tables
    def __setup_database(self):

        # self.db_cur.execute("""DROP TABLE IF EXISTS "Region" CASCADE""")
        # self.db_cur.execute("""DROP TABLE IF EXISTS "Video" """)

        # Create States table
        # TODO how to place hold Region table name
        self.db_cur.execute("""CREATE TABLE IF NOT EXISTS "Region" (
                       "Code" VARCHAR(8) UNIQUE PRIMARY KEY,
                       "Name" VARCHAR(40)
                       )""")
        self.db_conn.commit()

        # Create Sites table
        self.db_cur.execute("""CREATE TABLE IF NOT EXISTS "Video" (
                       "ID" VARCHAR(40) UNIQUE PRIMARY KEY,
                       "Title" VARCHAR(256),
                       "Kind" VARCHAR(8),
                       "Code" VARCHAR(8),
                       FOREIGN KEY ("Code") REFERENCES "Region" ("Code")
                       )""")
        self.db_conn.commit()

        print('Setup database complete')

    # insert information to database
    def insert(self, table, data_dict):
        column_names = data_dict.keys()
        print(data_dict)

        # generate insert into query string
        query = sql.SQL("""INSERT INTO "{0}"({1}) VALUES({2}) ON CONFLICT DO NOTHING """).format(
            sql.SQL(table),
            sql.SQL(', ').join(map(sql.Identifier, column_names)),
            sql.SQL(', ').join(map(sql.Placeholder, column_names))
        )
        query_string = query.as_string(self.db_conn)
        self.db_cur.execute(query_string, data_dict)
        self.db_conn.commit()

    def inner_join_query(self, target):
        self.db_cur.execute('''SELECT * FROM "Video" INNER JOIN "Region" on ("Video"."Code"=
                    "Region"."Code") WHERE "Region"."Name"=%s ''', (target,))
        result = self.db_cur.fetchall()
        response = []
        for pair in result:
            response.append(pair)
            print(pair)

        print(response)
        return response
