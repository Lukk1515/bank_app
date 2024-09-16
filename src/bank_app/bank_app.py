class BankAccount:
    def __init__(self, balance, account_number, account_holder):
        self.__balance = balance
        self.__account_number = account_number
        self.__account_holder = account_holder
        self.__transaction_history = []
        self.__overdraft_limit = 0

    def get_balance(self):
        return self.__balance

    def add_balance(self, amount):
        self.__balance += amount
        self.__transaction_history.append(f"Deposited {amount}")
        print(f"Deposited {amount}. Current balance: {self.__balance}")

    def card_payment(self, price):

        transaction = self.__balance - price

        if transaction < 0:
            raise ValueError("Transaction rejected. No funds in account.")

        self.__balance -= price
        self.__transaction_history.append(f"Withdraw {price}")
        print(f"Withdraw {price}. Current balance: {self.__balance}")

    def get_transaction_history(self):
        return "\n".join(self.__transaction_history)

    def transfer(self, amount, other_account):

        if self.__balance < amount:
            print("Transfer canceled. No funds in account.")
            return

        self.__balance -= amount
        other_account.__balance += amount
        self.__transaction_history.append(
            f"Transferred {amount} to account {other_account.__account_number}"
        )
        other_account.__transaction_history.append(
            f"Received {amount} from account {self.__account_number}"
        )
        print(
            f"Transferred {amount} to account {other_account.__account_number}. Current balance: {self.__balance}"
        )

    def print_statement(self):
        print(
            f"Completed transactions: {self.__transaction_history}. Current balance: {self.__balance}"
        )

    def apply_interest(self, interest_rate):
        interest = self.__balance * interest_rate
        self.__balance += interest
        self.__transaction_history.append(
            f"The accrued interest is {interest}. Current balance: {self.__balance}"
        )
        print(f"The account balance after adding interest is {self.__balance}")

    def change_account_holder(self, new_holder):
        self.__account_holder = new_holder
        self.__transaction_history.append(f"New holder the account is {new_holder}")
        print(f"New holder the account is {new_holder}")

    def set_overdraft_limit(self, limit):
        if limit < 0:
            raise ValueError("Overdraft limit cannot be negative.")
        self.__overdraft_limit = limit
        self.__transaction_history.append(f"Overdraft limit set to {limit}")
        print(f"Overdraft limit set to {limit}")
