import sqlite3
import json
import os


def load_words():
    con = sqlite3.connect('words.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            sentence TEXT NOT NULL
        )
    """)
    con.commit()
    cur.execute("SELECT COUNT(*) FROM words")
    if cur.fetchone()[0] > 0:
        con.close()
        return
    with open('data_words.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    for cat, words in data.items():
        for word, info in words.items():
            cur.execute("""
                INSERT INTO words (category, word, translation, sentence)
                VALUES (?, ?, ?, ?)
            """, (cat, word, info['translation'], info['sentence']))
    con.commit()
    con.close()