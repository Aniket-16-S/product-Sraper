import aiosqlite
import aiofiles
import os
from datetime import datetime

DB_NAME = "product_cache.db"


async def init_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS product_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                source TEXT,
                name TEXT,
                link TEXT,
                price TEXT,
                delivery TEXT,
                rating TEXT,
                image BLOB,
                timestamp TEXT,
                p_index INT
            )
        ''')
        await db.commit()


async def store_query_data(query, source, item):
    timestamp = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO product_cache (query, source, name, link, price, delivery, rating, image, timestamp, p_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            query,
            source,
            item.get("Name", "Unknown Product"),
            item.get("product_link", "N/A"),
            item.get("price", "N/A"),
            item.get("delivery", "N/A"),
            item.get("review", "N/A"),
            None,
            timestamp,
            item.get("index", -1)
        ))
        await db.commit()


async def cache_images(query):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT DISTINCT source FROM product_cache WHERE query = ?", (query,)) as cursor:
            srcs = [row[0] async for row in cursor]

        for src in srcs:
            async with db.execute("SELECT id, p_index FROM product_cache WHERE source = ? AND query = ?", (src, query)) as cursor:
                rows = [row async for row in cursor]

            for row_id, index in rows:
                img_path = os.path.join(src, query, f"product_{index}.jpg")
                if not os.path.exists(img_path):
                    print(f"Image not found at: {img_path}")
                    continue

                try:
                    async with aiofiles.open(img_path, "rb") as f:
                        img_blob = await f.read()
                    await db.execute("UPDATE product_cache SET image = ? WHERE id = ?", (img_blob, row_id))
                except Exception as e:
                    print(f"Failed to read/save image: {e}")

        await db.commit()


async def retrieve_query_data(query):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT DISTINCT source FROM product_cache WHERE query = ?", (query,)) as cursor:
            sources = [row[0] async for row in cursor]

        if not sources:
            print("No cache found for query:", query)
            return False

        for src in sources:
            print(f"\nSource: {src.upper()}")
            async with db.execute('''
                SELECT name, link, price, delivery, rating, image, timestamp, p_index
                FROM product_cache
                WHERE query = ? AND source = ?
            ''', (query, src)) as cursor:
                rows = [row async for row in cursor]

            if not rows:
                continue

            timestamp = rows[0][6]
            age = (datetime.utcnow() - datetime.fromisoformat(timestamp)).total_seconds() / 60
            print(f"Cached {len(rows)} products ({age:.1f} mins old)")

            if age > 2880:
                await db.execute("DELETE FROM product_cache WHERE query = ?", (query,))
                await db.commit()
                return False

            save_path = os.path.join(src, query)
            os.makedirs(save_path, exist_ok=True)
            product_count:int = -1
            for name, link, price, delivery, rating, img_blob, _, index in rows:
                product_count += 1
                print(f"\n===== Product {product_count} -- {src} =====")
                print(f"   Name    : {name}")
                print(f"   Link    : {link}")
                print(f"   Price   : {price}")
                print(f"   Delivery: {delivery}")
                print(f"   Rating  : {rating}")

                img_file = os.path.join(save_path, f"product{index}.jpg")
                try:
                    async with aiofiles.open(img_file, "wb") as f:
                        await f.write(img_blob)
                except Exception as e:
                    print(f"in cache.py problem while saving img as {e}")

    return True
