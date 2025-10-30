import sqlite3 as sql

class Connector:
    name_db = 'bonuses.db'

    def __init__(self, *args):
        self.name_db = self.name_db if len(args) == 0 else args[0]
        connection, cursor = self.__connection()
        self.__create_tables(connection, cursor)
        self.__disconnection(connection, cursor)

    def __connection(self):
        connection = sql.connect(self.name_db)
        return connection, connection.cursor()
    
    def __disconnection(self,connection,cursor):
        cursor.close()
        connection.close()
    
    def __create_tables(self, connection, cursor):
        Table =  """create table if not exists bonuses (
        id integer primary key autoincrement,
        code varchar(60) unique,
        project varchar(60),
        wager integer,
        maxwin integer,
        game varchar(60),
        provider varchar(60),
        price_RUB integer,
        price_KZT integer,
        price_UAH integer,
        count_spin integer,
        price_spin_RUB integer,
        price_spin_KZT integer,
        price_spin_UAH integer,
        date_start date,
        date_end date, 
        code_back varchar(60))"""  
        cursor.execute(Table)
        Table = """create table if not exists users (
        id integer primary key autoincrement,
        telegram int unique,
        acces boolean default false)"""
        cursor.execute(Table)
        try:
            cursor.execute('insert into users (telegram, acces) values(943464965,True)')
        except: pass
        connection.commit()
    
    def insert_bonus_info(self, *args):
        try:
            connection, cursor = self.__connection()
            cursor.execute(f'insert into bonuses (code, project, wager, maxwin, game, provider, price_RUB, price_KZT, price_UAH, count_spin, price_spin_RUB, price_spin_KZT, price_spin_UAH, date_start, date_end, code_back) values(\'{args[0]}\',\'{args[1]}\',{args[2]},\'{args[3]}\',\'{args[4]}\',\'{args[5]}\',{args[6]},{args[7]},{args[8]},{args[9]},{args[10]},{args[11]},{args[12]},\'{args[13]}\',\'{args[14]}\',\'{args[15]}\')')
            connection.commit()
            return True
        except Exception as ex:
            print(ex)
            return False
        finally:
            self.__disconnection(connection, cursor)
    
    def add_new_user(self, telegram):
        try:
            connection, cursor = self.__connection()
            cursor.execute(f'insert into users (telegram) values({telegram})')
            connection.commit()
            return True
        except:
            return False
        finally:
            self.__disconnection(connection, cursor)
    
    def add_acces_to_user(self, telegram):
        try:
            connection, cursor = self.__connection()
            cursor.execute(f'update users set acces = True where telegram = {telegram}')
            connection.commit()
            return True
        except:
            return False
        finally:
            self.__disconnection(connection, cursor)

    def check_acces(self, telegram):
        try:
            connection, cursor = self.__connection()
            cursor.execute(f'select acces from users where telegram = {telegram}')
            return cursor.fetchone()[0]
        except:
            return False
        finally:
            self.__disconnection(connection, cursor)        

    def get_bonus_info(self, code, currency = 'RUB'):
        try:
            connection, cursor = self.__connection()
            match currency:
                case 'RUB'  :   cursor.execute(f'select project, wager, maxwin, game, provider, price_RUB, count_spin, price_spin_RUB, date_start, date_end, code_back from bonuses where code = \'{code}\'')
                case 'KZT'  :   cursor.execute(f'select project, wager, maxwin, game, provider, price_KZT, count_spin, price_spin_KZT, date_start, date_end, code_back from bonuses where code = \'{code}\'')
                case 'UAH'  :   cursor.execute(f'select project, wager, maxwin, game, provider, price_UAH, count_spin, price_spin_UAH, date_start, date_end, code_back from bonuses where code = \'{code}\'')
            return cursor.fetchone()
        except Exception as ex:
            print(ex)
            return False
        finally:
            self.__disconnection(connection, cursor)
    
    def get_bonuses_info_from_project(self, project, currency = 'RUB'):
        try:
            connection, cursor = self.__connection()
            match currency:
                case 'RUB'  :   cursor.execute(f'select project, wager, maxwin, game, provider, price_RUB, count_spin, price_spin_RUB, date_start, date_end, code_back from bonuses where project = {project}')
                case 'KZT'  :   cursor.execute(f'select project, wager, maxwin, game, provider, price_KZT, count_spin, price_spin_KZT, date_start, date_end, code_back from bonuses where project = {project}')
                case 'UAH'  :   cursor.execute(f'select project, wager, maxwin, game, provider, price_UAH, count_spin, price_spin_UAH, date_start, date_end, code_back from bonuses where project = {project}')
            return cursor.fetchall()
        except:
            return False
        finally:
            self.__disconnection(connection, cursor)