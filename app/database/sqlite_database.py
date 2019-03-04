import sqlite3
import abc
from .base import Database

from logzero import logger

class SqliteDatabase(Database):

    def initialise(self, settings):
        logger.info("sqlite_database: initialise()")
        con = None

        create = False

        self.db_name = settings["db_name"]

        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute("SELECT * FROM records LIMIT 1")
            _ = cur.fetchone()
        except sqlite3.Error:
            # no table
            create = True
        finally:
            if con:
                con.close()

        if create:
            self.create_schema()
        else:
            logger.info("sqlite_database: schema ready")


    def create_schema(self):
        logger.debug("sqlite_database: create_schema()")
        con = None

        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute("CREATE TABLE records (id TEXT, timestamp TEXT, region TEXT, image_id TEXT, image_name TEXT, os TEXT, ecs_runtime_version TEXT, ecs_agent_version TEXT)")
            con.commit()
        except sqlite3.Error as e:
            logger.error("sqlite_database: problem during create_schema() - %s" % str(e))
        finally:
            if con:
                con.close()


    def top(self, num_results=10):
        logger.debug("sqlite_database: top()")
        con = None
        try:
            con = sqlite3.connect(self.db_name)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM records ORDER BY timestamp DESC LIMIT ?", (num_results,))
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            logger.error("sqlite_database: problem during top() - %s" % str(e))
            return None
        finally:
            if con:
                con.close()


    def all(self):
        logger.debug("sqlite_database: all()")
        con = None
        try:
            con = sqlite3.connect(self.db_name)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM records")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            logger.error("sqlite_database: problem during all() - %s" % str(e))
            return None
        finally:
            if con:
                con.close()


    def save(self, record):
        logger.debug("sqlite_database: save()")
        con = None
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute("INSERT INTO records VALUES (?,?,?,?,?,?,?,?)",
                (record.id, record.timestamp, record.region, record.image_id, record.image_name, record.os, record.ecs_runtime_version, record.ecs_agent_version))
            con.commit()
        except sqlite3.Error as e:
            logger.error("sqlite_database: problem during save() - %s" % str(e))
        finally:
            if con:
                con.close()


    def exists(self, record):
        logger.debug("sqlite_database: exists()")
        con = None
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute('''SELECT COUNT(*) FROM records WHERE id = ?''',
                (record.id,))
            data = cur.fetchone()
            return int(data[0]) > 0
        except sqlite3.Error as e:
            logger.error("sqlite_database: problem during exists() - %s" % str(e))
        finally:
            if con:
                con.close()


    def remove(self, record):
        logger.debug("sqlite_database: remove()")
        con = None
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute("DELETE FROM records WHERE id = ?", (record.id,))
            con.commit()
        except sqlite3.Error as e:
            logger.error("sqlite_database: problem during remove() - %s" % str(e))
        finally:
            if con:
                con.close()
