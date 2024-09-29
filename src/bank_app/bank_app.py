class BankAccount:
    def __init__(self, balance: float, account_number: str, account_holder: str):
        """Initialize a new bank account.

        Args:
            balance (float): Initial balance for the account.
            account_number (str): The account number.
            account_holder (str): The name of the account holder.
        """
        self.__balance = balance
        self.__account_number = account_number
        self.__account_holder = account_holder
        self.__transaction_history = []
        self.__overdraft_limit = 0

    def get_balance(self):
        """Retrieve the current balance of the bank account.

        Returns:
            float: The current balance.
        """
        return self.__balance

    def add_balance(self, amount: float):
        """Add a specified amount to the account balance and record the transaction.

        Args:
            amount (float): The amount to be deposited.
        """
        self.__balance += amount
        self.__transaction_history.append(f"Deposited {amount}")
        print(f"Deposited {amount}. Current balance: {self.__balance}")

    def card_payment(self, price: float):
        """Deduct a specified amount from the account for a card payment, if sufficient funds are available.

        Args:
            price (float): The amount to be withdrawn for the payment.

        Raises:
            ValueError: If the account balance is insufficient for the payment.
        """
        transaction = self.__balance - price

        if transaction < 0:
            raise ValueError("Transaction rejected. No funds in account.")

        self.__balance -= price
        self.__transaction_history.append(f"Withdraw {price}")
        print(f"Withdraw {price}. Current balance: {self.__balance}")

    def get_transaction_history(self):
        """Retrieve the transaction history of the account.

        Returns:
            str: A string representation of the transaction history.
        """
        return "\n".join(self.__transaction_history)

    def transfer(self, amount: float, other_account: str):
        """Transfer a specified amount to another bank account.

        Args:
            amount (float): The amount to be transferred.
            other_account (BankAccount): The target bank account to receive the funds.

        Raises:
            ValueError: If there are insufficient funds for the transfer.
        """
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

    def apply_interest(self, interest_rate: float):
        """Apply interest to the current balance and update the transaction history.

        Args:
            interest_rate (float): The interest rate to be applied to the current balance.
        """
        interest = self.__balance * interest_rate
        self.__balance += interest
        self.__transaction_history.append(
            f"The accrued interest is {interest}. Current balance: {self.__balance}"
        )
        print(f"The account balance after adding interest is {self.__balance}")

    def change_account_holder(self, new_holder: str):
        """Change the account holder's name and record the update in the transaction history.

        Args:
            new_holder (str): The new name of the account holder.
        """
        self.__account_holder = new_holder
        self.__transaction_history.append(f"New holder the account is {new_holder}")
        print(f"New holder the account is {new_holder}")

    def set_overdraft_limit(self, limit: float):
        """Set a new overdraft limit for the account.

        Args:
            limit (float): The new overdraft limit.

        Raises:
            ValueError: If the overdraft limit is negative.
        """
        if limit < 0:
            raise ValueError("Overdraft limit cannot be negative.")
        self.__overdraft_limit = limit
        self.__transaction_history.append(f"Overdraft limit set to {limit}")
        print(f"Overdraft limit set to {limit}")
