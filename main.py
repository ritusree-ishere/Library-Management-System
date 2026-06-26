print("Program started")

from book_manager import *

while True:
    print("\n1 Add")
    print("2 View")
    print("3 Update")
    print("4 Delete")
    print("5 Exit")
    print("6 Search")

    choice = input("\nEnter: ")

    if choice == "1":
        add_book(input("Title: "), input("Author: "), float(input("Price: ")))

    elif choice == "2":
        view_books()

    elif choice == "3":
        update_book(input("ID: "), {"title": input("New title: ")})

    elif choice == "4":
        delete_book(input("ID: "))

    elif choice == "5":
        break

    elif choice == "6":
        keyword = input("Enter title/author: ")
        search_books(keyword)