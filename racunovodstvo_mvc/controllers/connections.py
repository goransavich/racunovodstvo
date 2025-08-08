import mysql.connector as conn
from mysql.connector import Error
from racunovodstvo_mvc.views.greske import Greske
# Connect to database


class Database:

   con = None

   def __init__(self):
      try:
         self.con = conn.connect(host='localhost', database='racunovodstvo', user='root', password='UrLe19023009')
      except Error as e:
         Greske("Greska prilikom povezivanja na bazu", e)

   def select(self, tablename, select_columns, order=None):
      if (order==None):
         query_select = "SELECT {1} from {0}".format(tablename, select_columns)
      else:
         query_select = "SELECT {1} from {0} ORDER by {2}".format(tablename, select_columns, order)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_where(self, tablename, select_columns, condition, value, order=None):
      if (order==None):
         query_select = "SELECT {1} from {0} WHERE {2} = '{3}'".format(tablename, select_columns, condition, value)
      else:
         query_select = "SELECT {1} from {0} WHERE {3} = '{4}' ORDER by {2}".format(tablename, select_columns, order, condition, value)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_count(self, tablename, where_column, value, where_column2=None, value2=None):
      if (where_column2==None):
         query_select_count = "SELECT COUNT(*) FROM {0} WHERE {1} = '{2}'".format(tablename, where_column, value)
      else:
         query_select_count = "SELECT COUNT(*) FROM {0} WHERE {1} = '{2}' and {3} = '{4}'".format(tablename, where_column, value, where_column2, value2)
      cursor = self.con.cursor()
      cursor.execute(query_select_count)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_count_tree_conditions(self, tablename, where_column, value, where_column2, value2, where_column3, value3):
      query_select_count = "SELECT COUNT(*) FROM {0} WHERE {1} = '{2}' and {3} = '{4}' and {5} = '{6}'".format(tablename, where_column, value, where_column2, value2, where_column3, value3)
      cursor = self.con.cursor()
      cursor.execute(query_select_count)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_sum_group(self, tablenames, select_columns, condition, value, group, order=None):
      if (order==None):
         query_select_sum = "SELECT {1} from {0} WHERE {2} = {3} group by {4}".format(tablenames, select_columns, condition, value, group)
      else:
         query_select_sum = "SELECT {1} from {0} WHERE {2} = {3} group by {4} ORDER by {5}".format(tablenames, select_columns, condition, value, group, order)
      cursor = self.con.cursor()
      cursor.execute(query_select_sum)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def insert(self, tablename, schema, value):
      # ako vrednost value ima samo jednu kolonu, onda mora da se ukloni zarez na kraju tupla (npr. tabela nalozi)
      if len(value) == 1:
         values = str(value)[:-2] + str(value)[-1]
      else:
         values = value
      query_insert = "INSERT INTO {0} ({1}) VALUES {2}".format(tablename, schema, values)
      cursor = self.con.cursor()
      cursor.execute(query_insert)
      self.con.commit()
      cursor.close()
      self.con.close()

   def update(self, tablename, set_condition, filter_condition):
      query_update = "UPDATE {0} SET {1} WHERE {2}".format(tablename, set_condition, filter_condition)
      cursor = self.con.cursor()
      cursor.execute(query_update)
      self.con.commit()
      cursor.close()
      self.con.close()

   def delete(self, tablename, delete_condition):
      query_delete = "DELETE FROM {0} WHERE {1}".format(tablename, delete_condition)
      cursor = self.con.cursor()
      cursor.execute(query_delete)
      self.con.commit()
      cursor.close()
      self.con.close()

   def join(self, tablenames, select_columns, condition, value, condition2, value2, order=None):
      if (order==None):
         query_select = "SELECT {1} from {0} WHERE (({2}='{3}') AND ({4}={5}))".format(tablenames, select_columns, condition, value, condition2, value2)
      else:
         query_select = "SELECT {1} from {0} WHERE (({2}='{3}') AND ({4}={5})) ORDER by {6}".format(tablenames, select_columns, condition, value, condition2, value2, order)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_last(self, tablename, select_columns, condition, value):
      query_select = "SELECT {1} from {0} WHERE {2} = {3}".format(tablename, select_columns, condition, value)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_exists(self, tablename, condition, value):
      query_select = "SELECT EXISTS(SELECT * FROM {0} WHERE {1} LIKE '{2}%') ".format(tablename, condition, value)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_like(self, tablename, condition, value):
      query_select = "SELECT * FROM {0} WHERE {1} LIKE '{2}%' ".format(tablename, condition, value)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_in(self, tablename, condition, value):
      if type(value) == tuple:
         query_select = "SELECT * FROM {0} WHERE {1} in {2}".format(tablename, condition, value) # ako je niz vrednosti ne idu zagrade posto niz vec ima zagrade
      else:
         query_select = "SELECT * FROM {0} WHERE {1} in ({2})".format(tablename, condition, value) # ako je samo jedna vrednost konta onda idu zagrade
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_distinct(self, select_columns, iz_tabele,  join1, join2, where_condition, order_by, nivo=None):
      if nivo == None:
         query_select = "SELECT DISTINCT konto.oznaka as proba, {0} FROM {1} join {2} join {3} WHERE {4} GROUP BY proba ORDER BY proba".format(
            select_columns, iz_tabele, join1, join2, where_condition, order_by)
      else:
         query_select = "SELECT DISTINCT LEFT(konto.oznaka, {5}) as proba, {0} FROM {1} join {2} join {3} WHERE {4} GROUP BY proba ORDER BY proba".format(
            select_columns, iz_tabele, join1, join2, where_condition, nivo, order_by)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_distinct_dobavljaci(self, select_columns, iz_tabele,  join1, join2, where_condition, order_by, nivo=None):
      query_select = "SELECT DISTINCT substring(konto.oznaka, 8) as proba, {0} FROM {1} join {2} join {3} WHERE {4} GROUP BY proba ORDER BY proba".format(
            select_columns, iz_tabele, join1, join2, where_condition, nivo, order_by)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_where_join(self, select_columns, iz_tabele,  join1, join2, where_condition, order_by):
      query_select = "SELECT {0} FROM {1} join {2} join {3} WHERE {4} ORDER BY {5}".format(select_columns, iz_tabele,  join1, join2, where_condition, order_by)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_distinct_pojavljivanje(self, select_columns, iz_tabele):
      query_select = "SELECT DISTINCT {0} FROM {1}".format(select_columns, iz_tabele)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_distinct_izvrsenje(self, select_columns, iz_tabele,  join1, join2, where_condition, order_by, nivo):
      query_select = "SELECT DISTINCT LEFT(konto.oznaka, {5}) as proba, {0} FROM {1} join {2} join {3} WHERE {4} GROUP BY proba ORDER BY proba".format(
         select_columns, iz_tabele, join1, join2, where_condition, nivo, order_by)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

   def select_last_row(self, tablename, select_column, order):
      query_select = "SELECT {1} from {0} ORDER BY {2} DESC LIMIT 1".format(tablename, select_column, order)
      cursor = self.con.cursor()
      cursor.execute(query_select)
      rezultat = cursor.fetchall()
      cursor.close()
      self.con.close()
      return rezultat

############## OVO SAM NASAO U PETAK #################33
'''
import mysql

import mysql.connector
from mysql.connector import errorcode

class Mysql(object):
    __instance = None

    __host = None
    __user = None
    __password = None
    __database = None

    __session = None
    __connection = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Mysql, cls).__new__(cls)
        return cls.__instance

    def __init__(self, host='', user='', password='', database=''):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database

    #Open connection with database
    def _open(self):
        try:
            cnx = mysql.connector.connect(host=self.__host, user=self.__user, password=self.__password,
                                          database=self.__database)
            self.__connection = cnx
            self.__session = cnx.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Something is wrong with your user name or password')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Database does not exists')
            else:
                print(err)

    def _close(self):
        self.__session.close()
        self.__connection.close()

    def insert(self, table, *args, **kwargs):
        values = None
        query = "INSERT INTO %s " % table
        if kwargs:
            keys = kwargs.keys()
            values = kwargs.values()
            query += "(" + ",".join(["`%s`"]*len(keys)) % tuple(keys) + ") VALUES(" + ",".join(["%s"]*len(values)) + ")"
        elif args:
            values = args
            query += " VALUES(" + ",".join(["%s"]*len(values)) + ")"
        self._open()
        self.__session.execute(query, values)
        self.__connection.commit()
        self._close()
        return self.__session.lastrowid

    def select(self, table, where=None, *args):
        result = None
        query = "SELECT "
        keys = args
        l = len(keys) - 1
        for i, key in enumerate(keys):
            query += "`"+key+"`"
            if i < l:
                query += ","
        query += " FROM %s" % table
        if where:
            query += " WHERE %s" % where

        self._open()
        self.__session.execute(query)
        self.__connection.commit()
        for result in self.__session.stored_results():
            result = result.fetchall()
        self._close()
        return result

    def update(self, table, index, **kwargs):
        query = "UPDATE %s SET" % table
        keys = kwargs.keys()
        values = kwargs.values()
        l = len(keys) - 1
        for i, key in enumerate(keys):
            query += "`"+key+"`=%s"
            if i < l:
                query += ","
        query += " WHERE index=%d" % index
        self._open()
        self.__session.execute(query, values)
        self.__connection.commit()
        self._close()

    def delete(self, table, index):
        query = "DELETE FROM %s WHERE uuid=%d" % (table, index)
        self._open()
        self.__session.execute(query)
        self.__connection.commit()
        self._close()

    def call_store_procedure(self, name, *args):
        result_sp = None
        self._open()
        self.__session.callproc(name, args)
        self.__connection.commit()
        for result in self.__session.stored_results():
            result_sp = result.fetchall()
        self._close()
        return result_sp

##### A OVAKO RADI ########3
#from Mysql import Mysql
connection = Mysql(host='localhost', user='root', password='', database='test')
#Assuming that our table have the fields id and name in this order.
#we can use this way but the parameter should have the same order that table
#connection.insert('table_name',parameters to insert)
connection.insert('test',1, 'Alejandro Mora')
#in this case the order isn't matter
#connection.insert('table_name', field=Value to insert)
connection.insert('test',name='Alejandro Mora', id=1)
#connection.select('Table', where="conditional(optional)", field to returned)
connection.select('test', where="name = 'Alejandro Mora' ")
connection.select('test', None,'id','name')
#connection.update('Table', id, field=Value to update)
connection.update('test', 1, name='Alejandro')
#connection.delete('Table', id)
connection.delete('test', 1)
#connection.call_store_procedure(prodecure name, Values)
connection.call_store_procedure('search_users_by_name', 'Alejandro')
'''