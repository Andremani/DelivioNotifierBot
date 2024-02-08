import sqlite3

class SqliteDb:
    def __init__(self):
        try:
            self.dbconnection = sqlite3.connect('test_database.db')
        except sqlite3.Error:
            print("Can't find database")

        try:
            self.cursor = self.dbconnection.cursor()
        except sqlite3.Error:
            print("Can't get cursor")

        self.tables_creation()

    def __enter__(self):
        return self

    def tables_creation(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS Restaurants 
            (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL
            )'''
        self.cursor.execute(create_table_query)

        create_table_query = '''
            CREATE TABLE IF NOT EXISTS BotSubscribers 
            (
            chat_id INTEGER PRIMARY KEY
            )'''
        self.cursor.execute(create_table_query)

    def insert_hardcoded_restaurants(self):
        hardcoded_rows = [("1", "Anonimousy2", "anon2"), ("2", "B2", "b"), ("3", "C3", "c"), ("4", "D4", "d"), ("7", "E7", "e"), ("8", "F8", "f"), ("10", "G10", "g")]
        self.cursor.executemany('''INSERT OR IGNORE INTO Restaurants VALUES (?,?,?)''', hardcoded_rows)
        self.dbconnection.commit()

    def insert_hardcoded_subscribers(self):
        hardcoded_rows = [(1,), (2,), (3,), (4,), (7,), (8,), (10,)]
        self.cursor.executemany('''INSERT OR IGNORE INTO BotSubscribers VALUES (?)''', hardcoded_rows)
        self.dbconnection.commit()

    def select_existing_restaurants(self):
        self.cursor.execute('''SELECT id FROM Restaurants''')
        existing_restaurants_info = self.cursor.fetchall()
        return existing_restaurants_info

    def put_new_restaurants_in_database(self, new_restaurants):
        new_restaurants_rows = []
        for item in new_restaurants:
            new_restaurants_rows.append( (item.id, item.name, item.slug) )

        try:
            self.cursor.executemany('''INSERT OR IGNORE INTO Restaurants VALUES (?,?,?)''', new_restaurants_rows)
            self.dbconnection.commit()
        except:
            self.dbconnection.rollback()

    def put_new_subscribers_in_database(self, new_chats):
        new_chats_rows = []
        for chat_id in new_chats:
            new_chats_rows.append( (chat_id,) )

        try:
            self.cursor.executemany('''INSERT OR IGNORE INTO BotSubscribers VALUES (?)''', new_chats_rows)
            self.dbconnection.commit()
        except:
            self.dbconnection.rollback()

    def select_subscribers(self):
        self.cursor.execute('''SELECT chat_id FROM BotSubscribers''')
        chat_ids_tuple_list = self.cursor.fetchall()
        
        chat_ids = []
        for chat_id in chat_ids_tuple_list:
            chat_ids.append(chat_id[0])

        return chat_ids

    def clear_subscribers(self):
        clear_table_query = '''DELETE FROM BotSubscribers'''
        try:
            self.cursor.execute(clear_table_query)
            self.dbconnection.commit()
            self.cursor.execute('''VACUUM''')
            self.dbconnection.commit()
        except:
            self.dbconnection.rollback()

    def remove_subscriber(self, chat_id):
        clear_table_query = f'''DELETE FROM BotSubscribers WHERE chat_id = {chat_id}'''
        try:
            self.cursor.execute(clear_table_query)
            self.dbconnection.commit()
        except:
            self.dbconnection.rollback()

    def __exit__(self, *a): #self, exc_type, exc_value, traceback
        self.dbconnection.close()