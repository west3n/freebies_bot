import psycopg2

from database.connection import connect


async def add_to_favorite(advert_id, tg_id):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO freebies_favorite (ad_id, user_id) VALUES (%s, %s)", (advert_id, tg_id, ))
        db.commit()
    finally:
        cur.close()
        db.close()


async def get_all_favorites(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT ad_id FROM freebies_favorite WHERE user_id = %s", (tg_id,))
        all_ads = [ad[0] for ad in cur.fetchall()]
        try:
            cur.execute("SELECT * FROM freebies_advert WHERE id IN %s", (tuple(all_ads),))
        except psycopg2.Error:
            return None
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


async def remove_from_favorites(advert_id, tg_id):
    db, cur = connect()
    try:
        cur.execute("DELETE FROM freebies_favorite WHERE ad_id = %s AND user_id = %s", (advert_id, tg_id, ))
        db.commit()
    finally:
        cur.close()
        db.close()
