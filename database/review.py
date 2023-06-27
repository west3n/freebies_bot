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
