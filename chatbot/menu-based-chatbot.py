def show_menu():
    print("1. View balance")
    print("2. Transfer funds")
    print("3. Exit")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            print("Your account balance is $1000.")
        elif choice == "2":
            print("Funds transferred successfully.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
