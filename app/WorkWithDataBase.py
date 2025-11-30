import sqlite3
from contextlib import contextmanager

class WorkWithDatabase:
    # Фукнция реализует автоматическое открытие и закрытие подключения
    @contextmanager
    def get_connection(self):
        connection = sqlite3.connect('app/database.db')
        cursor = connection.cursor()
        try:
            yield cursor # выполнение запросов после yield
            connection.commit()
        except Exception:
            connection.rollback() # откат изменений в текущей транзакции
        finally:
            cursor.close()
            connection.close()

    def delete_from_products(self):
        connection = sqlite3.connect('app/database.db')
        cursor = connection.cursor()

        with self.get_connection() as cursor:
            cursor.execute("DELETE FROM products;")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='products';")

    def save_products(self, name: str, cost: int):
        with self.get_connection as cursor:
            cursor.execute("INSERT INTO products (name, cost) VALUES (?, ?);", (name, cost))

    def show_products(self):
        answer = None
        with self.get_connection() as cursor:
            cursor.execute("SELECT * FROM products;")
            answer = cursor.fetchall()

        return answer

    def show_product_for_id(self, id: int):
        answer = None
        with self.get_connection() as cursor:
            cursor.execute("SELECT name, cost FROM products WHERE id = ?;", (id,))
            answer = cursor.fetchone()

        return answer
    
    def insert_into_user_basket(self, chat_id: str, product_id: int, count: int):
        with self.get_connection() as cursor:
            cursor.execute("SELECT id, count FROM user_basket WHERE id_chat = ? AND id_product = ?;", (chat_id, product_id))
            existing_item = cursor.fetchone()
            
            if existing_item:
                new_count = existing_item[1] + count
                item_id = existing_item[0]
                cursor.execute("UPDATE user_basket SET count = ? WHERE id = ?;", (new_count, item_id))
            else:
                cursor.execute("INSERT INTO user_basket (id_chat, id_product, count) VALUES (?, ?, ?);", (chat_id, product_id, count))
            
    def select_busket(self, chat_id: str):
        answer = None
        with self.get_connection() as cursor:
            cursor.execute("SELECT * FROM user_basket WHERE id_chat = ?;", (chat_id,))
            answer = cursor.fetchall()

        return answer
    
    def delete_busket(self, chat_id: str):
        with self.get_connection() as cursor:
            cursor.execute("DELETE FROM user_basket WHERE id_chat = ?;", (chat_id,))
  
    def select_all_busket(self):
        answer = None
        with self.get_connection() as cursor:
            cursor.execute("SELECT * FROM user_basket;")
            answer = cursor.fetchall()
        
        return answer
    
    def delete_item_busket(self, item_id: int):
        with self.get_connection() as cursor:
            cursor.execute("DELETE FROM user_basket WHERE id = ?;", (item_id,))
   
    def update_item_count(self, item_id: int, new_count: int):
        with self.get_connection() as cursor:
            cursor.execute("UPDATE user_basket SET count = ? WHERE id = ?;", (new_count, item_id))