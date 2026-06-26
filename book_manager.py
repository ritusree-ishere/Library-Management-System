from firebase_config import db

def add_book(title, author, price):
    db.collection("books").add({
        "title": title,
        "author": author,
        "price": price
    })
    print("Book added!")

def view_books():
    docs = db.collection("books").stream()
    for doc in docs:
        print(doc.id, doc.to_dict())

def update_book(book_id, data):
    db.collection("books").document(book_id).update(data)

def delete_book(book_id):
    db.collection("books").document(book_id).delete()

def search_books(keyword):
    docs = db.collection("books").stream()
    found = False

    for doc in docs:
        data = doc.to_dict()
        if keyword.lower() in data["title"].lower() or keyword.lower() in data["author"].lower():
            print(doc.id, data)
            found = True

    if not found:
        print("No matching books found")