import sqlite3
import json

import sqlite3
import bcrypt

def init_database():
    try:
        # Чтение данных из JSON-файла
        with open(r'flipkart_fashion_products_dataset.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        # Подготовка данных для вставки
        formatted_products = []

        for product in products_data:
            try:
                # Преобразование цены (удаляем запятые и преобразуем в float)
                price = product.get('selling_price', 0)
                price = float(price) if price != None else 0
                
                # Извлечение процента скидки
                discount = float(product.get('discount', 0))
                
                # Преобразование рейтинга
                rating = float(product.get('average_rating', 0))
                
                # Определение наличия на складе
                stock = int(product.get('stock', 0))

                category = product.get('category', '')

                # Извлечение занчения поля пол
                sex = product.get('sex', ['unisex'])[0]
                if sex == 'Мужской' and category == 'Одежда':
                    category = 'Мужская одежда'
                elif sex == 'Женский':
                    category = 'Женская одежда'

                formatted_products.append((
                    product.get('title', ''),
                    product.get('description', ''),
                    price,
                    discount,
                    rating,
                    stock,
                    product.get('brand', ''),
                    category,
                    product.get('subcategory', '')
                ))
            except Exception as e:
                print(f"Ошибка обработки продукта {product.get('pid')}: {e}")

        # Создание базы данных
        conn = sqlite3.connect('shopping_assistant.sqlite')
        cursor = conn.cursor()
        
        # Удаление старых таблиц
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS cart")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Создание новых таблиц
        cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL,
            discountPercentage REAL DEFAULT 0.0,
            rating REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0,
            brand TEXT,
            category TEXT,
            subcategory TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            user_id TEXT,
            product_id INTEGER,
            quantity INTEGER,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        ''')
        
        # Вставка данных
        cursor.executemany(''' 
            INSERT INTO products 
            (title, description, price, discountPercentage, rating, stock, brand, category, subcategory) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
        ''', formatted_products)
        
        conn.commit()
        conn.close()
        print(f"База данных успешно инициализирована! Загружено {len(formatted_products)} записей.")
        return True
    
    except Exception as e:
        print(f"Критическая ошибка при инициализации базы данных: {e}")
        return False

if __name__ == '__main__':
    init_database()