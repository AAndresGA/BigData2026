from pymongo import MongoClient


def main() -> None:
    client = MongoClient("mongodb://admin:admin123@mongo:27017/")
    db = client["bigdata_course"]
    collection = db["events"]

    collection.insert_one({"source": "seed", "status": "ok"})
    print(collection.count_documents({}))


if __name__ == "__main__":
    main()
