"""The base command."""
import getpass
import sqlite3
import re
import datetime
from .color import *
from colorama import init
from colorama import Fore, Back, Style
# init()

class Base(object):
    """A base command."""
    table_name = "todo"
    category_name = "categories"

    def __init__(self, options):
        self.options = options

        username = getpass.getuser() + "/Documents"
        self.conn = sqlite3.connect("/Users/"+username+"/Schedule.db")
        self.cur = self.conn.cursor()

        self.create_todo_table()
        self.create_category_table()

        self.add_category("")

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')

    def check_input(self, option = 0):
        due_check = re.compile("^([0-9]{4}-[0-9]{2}-[0-9]{2})|x|-$")
        v_check = re.compile("^0|1|-$")
        due = self.options['<due>']
        v = self.options["<v>"]
        ctgr = self.options['<ctgr>']
        if not ctgr:
            ctgr= ""

        if option == 0: # check due
            if due_check.match(due):
                if not self.check_category(ctgr):
                    self.add_category(ctgr)
                return self.date_verify(due)
            else:
                return False
        elif option == 1: # check due, v
            if due_check.match(due) and v_check.match(v):
                if not self.check_category(ctgr):
                    self.add_category(ctgr)
                return self.date_verify(due)
            else:
                return False

    def add_todo(self):
        what = self.options['<what>']
        ctgr = self.options['<ctgr>']
        due = self.options['<due>']
        if not ctgr:
            ctgr= ""

        sql = "insert into '{0}' (what, due, category, finished) values ('{1}', '{2}', '{3}', {4})".format(
            self.table_name,
            what, due, ctgr, 0
        )
        self.cur.execute(sql)
        self.conn.commit()
    
    def check_ignore(self, i):
        args = [self.options['<what>'], self.options['<due>'], self.options['<ctgr>'], self.options['<v>']]
        return args[i] == "-"
  
    def update_todo(self, i):
        id = self.options['<id>']
        args = [self.options['<what>'], self.options['<due>'], self.options['<ctgr>'], self.options['<v>']]

        if i == 0:
            insql = "what='{}'".format(args[0])
        if i == 1:
            insql = "due='{}'".format(args[1])
        if i == 2:
            insql = "category='{}'".format(args[2])
        if i == 3:
            insql = "finished={}".format(args[3])
        
        sql = "UPDATE {0} set {1} where id={2}".format(
            self.table_name,
            insql,
            id
        )
        self.cur.execute(sql)
        self.conn.commit()

    def check_category(self, input_category):
        sql = "select * from '{}' where category='{}'".format(
            self.category_name,
            input_category
        )
        try:
            self.cur.excute(sql)
        except:
            return False
        return True

    def add_category(self, new_category):
        sql = "insert into '{}' (category) values ('{}')".format(
            self.category_name,
            new_category
        )

    def remove_row(self, table_name, id):
        sql = "DELETE FROM '{}' WHERE id={}".format(table_name, id)
        self.cur.execute(sql)
        self.conn.commit()

    def get_max_column(self,columns):
        return max(map(get_width,columns))

    def show(self, category=None, done=None):
        # done :== 0 | 1
        if category == None:
            if done == None:
                sql = "select * from '{}' where 1".format(self.table_name)
            else:
                sql = "select * from '{}' where finished={}".format(self.table_name, done)
        else:
            if done == None:
                sql = "select * from '{}' where category='{}'".format(self.table_name, category)
            else:
                sql = "select * from '{}' where category='{}' and finished={}".format(self.table_name, category, done)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        id_max = 3
        whats = ["Todo"]
        dues = ["Due"]
        categories = ["Category"]
        for row in rows:
            whats.append(row[1])
            dues.append(row[2])
            categories.append(row[3])
        what_max = self.get_max_column(whats)
        due_max = self.get_max_column(dues)
        category_max = self.get_max_column(categories)
        fin_max = 3

        print("┌",end="")
        print("─"* id_max,end="")
        print("┬",end="")
        print("─"* what_max,end="")
        print("┬",end="")
        print("─"* due_max,end="")
        print("┬",end="")
        print("─"* category_max,end="")
        print("┬",end="")
        print("─"* fin_max,end="")
        print("┐")

        print('│',end="")
        print(preformats("ID",id_max,'^'),end="")
        print('│',end="")
        print(preformats("Todo",what_max,'^'),end="")
        print('│',end="")
        print(preformats("Due",due_max,'^'),end="")
        print('│',end="")
        print(preformats("Category",category_max,'^'),end="")
        print('│',end="")
        print(preformats("F",fin_max,'^'),end="")
        print('│')

        print("├",end="")
        print("─"* id_max,end="")
        print("┼",end="")
        print("─"* what_max,end="")
        print("┼",end="")
        print("─"* due_max,end="")
        print("┼",end="")
        print("─"* category_max,end="")
        print("┼",end="")
        print("─"* fin_max,end="")
        print("┤")
        # print("└",end="")
        # print("┘")
        # print("┴",end="")

        for row in rows:
            
            print('│',end="")
            if row[4] == 1:
                print(Fore.BLACK+Back.WHITE+Style.BRIGHT+preformats(str(row[0]),id_max,'^'),end="")
            else:
                print(preformats(str(row[0]),id_max,'^'),end="")
            print('│',end="")
            print(preformats(row[1],what_max,'^'),end="")
            print('│',end="")
            print(preformats(row[2] if row[2] != 'x' else "",due_max,'^'),end="")
            print('│',end="")
            print(preformats(row[3],category_max,'^'),end="")
            print('│',end="")
            print(preformats(str(row[4]),fin_max,'^'),end="")
            
            if row[4] == 1:
                print(Style.RESET_ALL+'│')
            else:
                print('│')

        print("└",end="")
        print("─"* id_max,end="")
        print("┴",end="")
        print("─"* what_max,end="")
        print("┴",end="")
        print("─"* due_max,end="")
        print("┴",end="")
        print("─"* category_max,end="")
        print("┴",end="")
        print("─"* fin_max,end="")
        print("┘")
    
    def delete(self):
        id = self.options['<id>']
        self.remove_row(self.table_name,id)
        self.show()

    def create_todo_table(self):
        sql = """create table if not exists '{}' (
        id integer primary key autoincrement,
        what text not null,
        due text not null,
        category text not null,
        finished integer);""".format(self.table_name)

        self.cur.execute(sql)
        self.conn.commit()

    def create_category_table(self):
        sql = """create table if not exists '{}' (
            id integer primary key autoincrement,
            category text not null
        );""".format(self.category_name)
        self.cur.execute(sql)
        self.conn.commit()

    def drop_table(self, name):
        sql = """DROP TABLE '{}'""".format(name)
        self.cur.execute(sql)
        self.conn.commit()

    def date_verify(self, date_str):
        try:
            _ = datetime.datetime(int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10]))
            return True
        except ValueError:
            if date_str == 'x' or date_str == '-':
                return True
            else:
                return False

"""
3 x 10 y 3 6 = 22 + x + y >= 33
x >= 4 y >= 7
"""