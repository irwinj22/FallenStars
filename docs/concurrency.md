# Concurrency Cases

## Case 1: Credits

```mermaid
sequenceDiagram
    participant T1 as "Transaction 1"
    participant Database
    participant T2 as "Transaction 2"
    Note over T1, T2: Alice's (account id 1) Balance is $10
    T1->>Database: Get current balance
    T1->>Database: cur_balance = conn.execute(sqlalchemy.select(accounts.c.balance).where(accounts.c.id == 1)).scalar_one();
    T2->>Database: Alice transfers an additional $40 to her account.
    T2->>Database: UPDATE accounts SET balance = balance + 40 WHERE name = 'Alice'
    Note over T1, T2: Alice's Balance is now $50
    T1->>Database: Deduct book cost ($10) from balance
    T1->>Database: conn.execute(sqlalchemy.update(accounts).where(accounts.c.id == 1).values(balance = cur_balance - book_cost(conn, item_purchased_id)))
    Note over T1, T2: Alice's Balance should be $40, but is now $0 due to lost update.
```
## Case 2: Items


## Case 3: Mods
