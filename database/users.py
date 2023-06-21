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
        cur.execute("INSERT INTO freebies_userprofile (tg, username, fullname, contact, region, city) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
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


async def update_region(region, city):
    db, cur = connect()
    try:
        cur.execute("UPDATE freebies_userprofile SET region = %s, city = %s", (region, city))
        db.commit()
    finally:
        db.close()
        cur.close()
