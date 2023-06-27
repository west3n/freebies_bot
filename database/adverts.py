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


async def save_new_advert(date, author, region, city, category, photos, caption, delivery, payer):
    db, cur = connect()
    try:
        cur.execute(f"INSERT INTO freebies_advert (date, author_id, region, city, category_id, "
                    f"photos, caption, delivery, payer, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    f"RETURNING id",
                    (date, author, region, city, category, photos, caption, delivery, payer, 'active', ))
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


async def search_adverts(tg_id, city, caption, category_id):
    db, cur = connect()
    try:
        query = "SELECT * FROM freebies_advert WHERE author_id != %s "
        params = [tg_id]

        if city == 'Россия':
            query += "AND city IS NOT NULL "
        elif city:
            query += "AND city = %s "
            params.append(city)

        if caption == 'Любые слова':
            query += "AND caption IS NOT NULL "
        elif caption:
            query += "AND "
            if isinstance(caption, str):
                if len(caption.split(",")) == 1:
                    query += "LOWER(caption) LIKE LOWER(%s) OR "
                    params.append(f'%{caption.lower()}%')
                else:
                    caption_list = caption.split(",")
                    for word in caption_list:
                        query += "LOWER(caption) LIKE LOWER(%s) OR "
                        params.append(f'%{word.lower()}%')
            else:
                for word in caption:
                    query += "LOWER(caption) LIKE LOWER(%s) OR "
                    params.append(f'%{word.lower()}%')
            query = query[:-3]

        if category_id == "Все категории":
            query += "AND category_id IS NOT NULL "
        elif category_id:
            query += "AND category_id = %s "
            params.append(category_id)

        query += "AND status = 'active' ORDER BY date"
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


async def get_username_by_advert_id(advert_id):
    db, cur = connect()
    try:
        cur.execute("SELECT author_id FROM freebies_advert WHERE id = %s", (advert_id, ))
        tg_id = cur.fetchone()
        cur.execute("SELECT username, contact FROM freebies_userprofile WHERE tg = %s", (str(tg_id[0]), ))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def get_advert_data(advert_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM freebies_advert WHERE id = %s", (advert_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def delete_advert(advert_id):
    db, cur = connect()
    try:
        cur.execute("DELETE FROM freebies_advert WHERE id = %s", (advert_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_user_adverts(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM freebies_advert WHERE author_id = %s", (tg_id,))
        return cur.fetchall()
    finally:
        db.close()
        cur.close()


async def change_status(ad_id, status):
    db, cur = connect()
    try:
        cur.execute("UPDATE freebies_advert SET status = %s WHERE id = %s", (status, ad_id, ))
        db.commit()
    finally:
        db.close()
        cur.close()
