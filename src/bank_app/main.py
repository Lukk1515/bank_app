from bank_app import BankAccount


def main():
    account1 = BankAccount(1000, "123456789", "John Doe")
    account2 = BankAccount(560, "987654321", "Jane Smith")
    account3 = BankAccount(2000, "111222333", "Kate Miller")

    account1.transfer(300, account2)
    account1.get_transaction_history()
    account2.get_transaction_history()
    account1.get_balance()
    account2.get_balance()
    account1.add_balance(600)
    account2.add_balance(140)
    account1.print_statement()
    account2.print_statement()
    account3.transfer(3000, account2)
    account3.apply_interest(0.5)
    account2.change_account_holder("Samanta Flower")
    account2.print_statement()
    account1.set_overdraft_limit(1500)
    account2.get_transaction_history()


if __name__ == "__main__":
    main()
