import json
import os

from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "interview_prep")
COLLECTION_NAME = "questions"
DATA_FILE = "data/question_bank.json"


def seed():
    with open(DATA_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION_NAME]

    inserted = 0
    skipped = 0

    for q in questions:
        qid = q["id"]
        try:
            col.insert_one({"_id": qid, **q})
            inserted += 1
            print(f"  Inserted: {qid}")
        except errors.DuplicateKeyError:
            skipped += 1
            print(f"  Skipped (duplicate): {qid}")

    client.close()
    print(f"\nDone. {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    seed()
