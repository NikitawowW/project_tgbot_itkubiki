import sqlite3

class WorkWithDatabase:
    
    def delete_from_products(self):
        connection = sqlite3.connect('app/database.db')
        cursor = connection.cursor()

        cursor.execute("DELETE FROM products;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='products';")
        connection.commit()

        cursor.close()
        connection.close()

    def save_products(self, name: str, cost: int):
        connection = sqlite3.connect('app/database.db')

        cursor = connection.cursor()

        cursor.execute("INSERT INTO products (name, cost) VALUES (?, ?);", (name, cost))
        connection.commit()
        cursor.close()
        connection.close()
    
    def show_products(self):
        connection = sqlite3.connect('app/database.db')

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products;")
        answer = cursor.fetchall()

        cursor.close()
        connection.close()

        return answer

    def show_product_for_id(self, id: int):
        connection = sqlite3.connect('app/database.db')

        cursor = connection.cursor()

        cursor.execute("SELECT name FROM products WHERE id = ?;", (id,))
        answer = cursor.fetchone()

        cursor.close()
        connection.close()

        return answer[0]
    
    def insert_into_user_basket(self, chat_id: str, product_id: int, count: int):
        connection = sqlite3.connect('app/database.db')

        cursor = connection.cursor()

        cursor.execute("INSERT INTO user_basket (id_chat, id_product, count) VALUES (?, ?, ?);", (chat_id, product_id, count))
        connection.commit()
        cursor.close()
        connection.close()
    
    def select_busket(self, chat_id: str):
        connection = sqlite3.connect('app/database.db')

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user_basket WHERE id_chat = ?;", (chat_id,))
        answer = cursor.fetchall()

        cursor.close()
        connection.close()

        return answer
    
    def delete_busket(self, chat_id: str):
        connection = sqlite3.connect('app/database.db')
        cursor = connection.cursor()

        cursor.execute("DELETE FROM user_basket WHERE id_chat = ?;", (chat_id,))
        connection.commit()

        cursor.close()
        connection.close()
        
    def select_all_busket(self):
        connection = sqlite3.connect('app/database.db')
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user_basket;")
        answer = cursor.fetchall()

        cursor.close()
        connection.close()

        return answer