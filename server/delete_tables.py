import sqlite3

def clear_tables():
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('pizzeria.db')
        cursor = conn.cursor()
        
        # Удаление данных из таблиц
        cursor.execute("DELETE FROM order_items;")
        cursor.execute("DELETE FROM orders;")
        cursor.execute("DROP TABLE orders;")
        cursor.execute("DROP TABLE order_items;")
        
        # Подтверждение изменений
        conn.commit()
        print("Данные успешно удалены из таблиц orders и order_items.")
        
    except sqlite3.Error as e:
        print(f"Ошибка при работе с SQLite: {e}")
        
    finally:
        # Закрытие соединения
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто.")

# Вызов функции
clear_tables()