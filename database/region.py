import asyncio

from database.connection import connect


async def get_first_letters():
    db, cur = connect()
    try:
        cur.execute("SELECT DISTINCT SUBSTRING(name, 1, 1) AS first_letter FROM region ORDER BY first_letter ASC")
        return [letter[0] for letter in cur.fetchall()]
    finally:
        db.close()
        cur.close()


async def get_regions_by_first_letter(letter):
    db, cur = connect()
    try:
        cur.execute(f"SELECT name FROM region WHERE name LIKE '{letter}%'")
        return [region[0] for region in cur.fetchall()]
    finally:
        cur.close()
        db.close()


async def get_cities_by_region(region):
    db, cur = connect()
    try:
        cur.execute("SELECT id_region FROM region WHERE name = %s", (region, ))
        region_id = cur.fetchone()
        cur.execute("SELECT name from city WHERE id_region = %s", (region_id[0], ))
        return [city[0] for city in cur.fetchall()]
    finally:
        cur.close()
        db.close()

