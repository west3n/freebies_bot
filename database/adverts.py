import asyncio

from database.connection import connect


async def get_category_list():
    db, cur = connect()
    try:
        cur.execute(f"SELECT category FROM freebies_category ORDER BY category")
        return [category[0] for category in cur.fetchall()]
    finally:
        cur.close()
        db.close()


async def save_new_advert(data, author, region, city, category, photos, caption, delivery, payer):
    db, cur = connect()
    try:
        cur.execute(f"INSERT INTO freebies_advert (date, author_id, region, city, category_id, "
                    f"photos, caption, delivery, payer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (data, author, region, city, category, photos, caption, delivery, payer, ))
        db.commit()
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def get_amount_by_date_and_user(date, user):
    db, cur = connect()
    try:
        cur.execute(f"SELECT COUNT(*) FROM freebies_advert WHERE date = %s AND author_id = %s", (date, user, ))
        return cur.fetchone()
    finally:
        cur.close()
        db.close()


async def get_explicit_words():
    db, cur = connect()
    try:
        cur.execute(f"SELECT word FROM freebies_explicitwords ORDER BY word")
        return [word[0] for word in cur.fetchall()]
    finally:
        cur.close()
        db.close()
