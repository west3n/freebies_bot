import asyncio

from database.connection import connect


async def new_review(author_id, user_id, text):
    db, cur = connect()
    try:
        cur.execute("INSERT INTO freebies_review (author_id, user_id, text) VALUES (%s, %s, %s)",
                    (author_id, user_id, text, ))
        db.commit()
    finally:
        db.close()
        cur.close()


async def get_user_review(user_id):
    db, cur = connect()
    try:
        cur.execute("SELECT text, author_id FROM freebies_review WHERE user_id = %s", (user_id,))
        return cur.fetchall()
    finally:
        db.close()
        cur.close()


async def get_user_author_review(user_id, author_id):
    db, cur = connect()
    try:
        cur.execute("SELECT * FROM freebies_review WHERE user_id = %s AND author_id = %s", (user_id, author_id, ))
        return cur.fetchone()
    finally:
        db.close()
        cur.close()
