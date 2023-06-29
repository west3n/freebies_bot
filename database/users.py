import asyncio

from database.connection import connect


async def get_users_list():
    db, cur = connect()
    try:
        cur.execute("SELECT tg FROM freebies_userprofile")
        return [user[0] for user in cur.fetchall()]
    finally:
        db.close()
        cur.close()


async def get_blocked_users_list():
    db, cur = connect()
    try:
        cur.execute("SELECT blocked_user_id FROM freebies_blockedusers")
        return [user[0] for user in cur.fetchall()]
    finally:
        db.close()
        cur.close()


async def get_block_reason(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT reason FROM freebies_blockedusers WHERE blocked_user_id = %s", (tg_id, ))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def add_new_user(tg, username, fullname, contact, region, city):
    db, cur = connect()
    if not contact:
        contact = "Нет контакта"
    try:
        cur.execute("INSERT INTO freebies_userprofile (tg, username, fullname, contact, region, city, rating) "
                    "VALUES (%s, %s, %s, %s, %s, %s, 0)",
                    (tg, username, fullname, contact, region, city))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_user_data(tg_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM freebies_userprofile WHERE tg=%s", (tg_id, ))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def update_region(region, city, tg_id):
    db, cur = connect()
    try:
        cur.execute("UPDATE freebies_userprofile SET region = %s, city = %s WHERE tg = %s", (region, city, tg_id))
        db.commit()
    finally:
        db.close()
        cur.close()


async def block_user(tg_id, reason):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO freebies_blockedusers (blocked_user_id, reason) VALUES (%s, %s)", (tg_id, reason,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def new_agreement(author_id, user_id, ad_id):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO freebies_agreements (author_id, user_id, ad_id) VALUES (%s, %s, %s)",
                    (author_id, user_id, ad_id, ))
        db.commit()
    finally:
        db.close()
        cur.close()


async def delete_agreement(author_id, ad_id):
    db, cur = connect()
    try:
        cur.execute("DELETE FROM freebies_agreements WHERE author_id = %s AND ad_id = %s",
                    (author_id, ad_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_agreement_users(ad_id):
    db, cur = connect()
    try:
        cur.execute("SELECT id, author_id, user_id FROM freebies_agreements WHERE ad_id = %s", (ad_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def get_agreement_data(agreement_id):
    db, cur = connect()
    try:
        cur.execute("SELECT ad_id, author_id, user_id FROM freebies_agreements WHERE id = %s", (agreement_id,))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()


async def update_user_rating(user_id, grade):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO freebies_userrating (user_id, grade) VALUES (%s, %s)", (user_id, grade,))
        db.commit()
        cur.execute("SELECT AVG(grade) FROM freebies_userrating WHERE user_id = %s", (user_id, ))
        grade = cur.fetchone()
        rounded_grade = round(grade[0], 1)
        cur.execute("UPDATE freebies_userprofile SET rating = %s WHERE tg = %s", (rounded_grade, user_id,))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_grade_amount(user_id):
    db, cur = connect()
    try:
        cur.execute("SELECT COUNT(grade) FROM freebies_userrating WHERE user_id = %s", (user_id,))
        grade_amount = cur.fetchone()
        return grade_amount[0]
    finally:
        db.close()
        cur.close()
