import sqlite3
import json
import csv
import sys
import os
import inspect

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def connectDB():
    try:
        path = os.path.dirname(os.path.realpath(__file__)) + "/database.db"
        con = sqlite3.connect(path)
        return con
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))


def createDB():
    con = connectDB()
    cursor = con.cursor()
    cursor.execute( """
        CREATE TABLE IF NOT EXISTS "programs" (
                "name"	TEXT NOT NULL,
                "exec"	TEXT UNIQUE,
                "location"	TEXT,
                "description"	TEXT,
                "uses"	INTEGER DEFAULT 0
        ); """
    )
    con.commit()
    cursor.close()
    con.close()

def update():
    try:
        con = connectDB()
        cursor = con.cursor()
        with open("/tmp/mydmenu_update_file.csv") as ifile:
            reader = csv.reader(ifile,delimiter = ',')
            for f in reader:
                cursor.execute( """ INSERT INTO programs
                 (name,exec,location,description) VALUES (?, ?, ?, ? )
                 ON CONFLICT(location) DO UPDATE SET
                 name= ? , exec= ? , location= ? , description= ?
                 """ , (f[0],f[1],f[2],f[3],f[0],f[1],f[2],f[3]) )
        con.commit()
        cursor.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
        print(error)
    finally:
        if con:
            con.close()


def clean_up(p):
    try:
        con = connectDB()
        cursor = con.cursor()
        str_query = """ DELETE FROM programs WHERE location = ? """
        cursor.execute(str_query, (p,) )
        con.commit()
        cursor.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def increment(p):
    try:
        con = connectDB()
        cursor = con.cursor()
        str_query = """ UPDATE programs SET uses = uses + 1 WHERE name = ? """
        cursor.execute(str_query, (p,) )
        con.commit()
        cursor.close()
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def get():
    try:
        con = connectDB()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        str_query = """ SELECT * from programs ORDER BY uses DESC """
        cursor.execute(str_query)
        rows = cursor.fetchall()
        cursor.close()
        print(json.dumps( [ dict(x) for x in rows] ))
    except sqlite3.Error as error:
        eprint("@%s: %s" % (inspect.stack()[0][3], error))
    finally:
        if con:
            con.close()


def myfuncSwitch(arg):
    cmd = arg[1]
    switcher = {
        "update": update,
        "get": get,
        "del": clean_up,
        "increment": increment,
    }
    func = switcher.get(cmd)
    func(*arg[2:])


if __name__ == "__main__":
    createDB()
    myfuncSwitch(sys.argv)
