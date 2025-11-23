import sqlite3
import os

class SaveData:
    def __init__(self, path="game.db"):
        self.path = path
        self.make_bd()

    def add_column(self, table, col, col_type):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        if col not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        con.commit()
        con.close()

    def make_bd(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        # счет
        cur.execute("""
            CREATE TABLE IF NOT EXISTS score (
                id INTEGER PRIMARY KEY,
                points INTEGER
            )
        """)
        cur.execute("SELECT COUNT(*) FROM score")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO score VALUES (1, 0)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                word TEXT PRIMARY KEY,
                done INTEGER
            )
        """)
        # слова
        cur.execute("""
            CREATE TABLE IF NOT EXISTS words (
                word TEXT PRIMARY KEY,
                category TEXT,
                translation TEXT,
                sentence TEXT
            )
        """)
        # бонус
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bonus (
                id INTEGER PRIMARY KEY,
                unlocked INTEGER
            )
        """)
        cur.execute("SELECT COUNT(*) FROM bonus")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO bonus (id, unlocked) VALUES (1, 0)")

        cur.execute("CREATE TABLE IF NOT EXISTS settings (dummy INTEGER)")
        con.commit()
        con.close()
        self.add_column("settings", "id", "INTEGER")
        self.add_column("settings", "hard_mode", "INTEGER")
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM settings")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO settings (id, hard_mode) VALUES (1, 0)")
        else:
            cur.execute("UPDATE settings SET id=1 WHERE id IS NULL")
            cur.execute("UPDATE settings SET hard_mode=0 WHERE hard_mode IS NULL")
        con.commit()
        con.close()

    def get_words(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT word, category, translation, sentence FROM words")
        rows = cur.fetchall()
        con.close()
        data = {}
        for w, c, tr, s in rows:
            if c not in data:
                data[c] = {}
            data[c][w] = {"translation": tr, "sentence": s}
        return data

    def add_word(self, word, category, tr, sent):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO words VALUES (?, ?, ?, ?)",
            (word, category, tr, sent)
        )
        con.commit()
        con.close()

    def get_points(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT points FROM score WHERE id=1")
        pnt = cur.fetchone()[0]
        con.close()
        return pnt

    def add_points(self, delta):
        pnt = self.get_points()
        pnt = max(0, pnt + delta)
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("UPDATE score SET points=?", (pnt,))
        con.commit()
        con.close()

    def mark(self, word):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO progress (word, done) VALUES (?, 1)",
            (word,)
        )
        con.commit()
        con.close()

    def get_done(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT word FROM progress WHERE done=1")
        rows = cur.fetchall()
        con.close()
        tmp = {row[0] for row in rows}
        return tmp

    def reset_words(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("DELETE FROM progress")
        con.commit()
        con.close()


    def is_unlocked(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT unlocked FROM bonus WHERE id=1")
        status = cur.fetchone()[0]
        con.close()
        if status:
            return True
        return False

    def unlock_bonus(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("UPDATE bonus SET unlocked=1 WHERE id=1")
        con.commit()
        con.close()


    def hard_mode(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT hard_mode FROM settings WHERE id=1")
        val = cur.fetchone()[0]
        con.close()
        return bool(val)

    def Ishard_mode(self, value: bool):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute(
            "UPDATE settings SET hard_mode=? WHERE id=1",
            (1 if value else 0,)
        )
        con.commit()
        con.close()
