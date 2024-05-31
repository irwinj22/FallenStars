# Concurrency Cases

## Case 1: Credits

mermaid`sequenceDiagram
    participant T1
    participant Database
    participant T2
    Note over T1, T2: Alice's (account id 1) Balance is 10
    T1->>Database: Get current balance
    T1->>Database: cur_balance = conn.execute(sqlalchemy.select(accounts.c.balance)<br>.where(accounts.c.id == 1)).scalar_one();
    T2->>Database: Alice transfers an additional $40 to her account.
    T2->>Database: UPDATE accounts SET balance = balance + 40 WHERE name = 'Alice'
    Note over T1, T2: Alice's Balance is $10 + $40 = $50
    T1->>Database: Deduct book cost ($10) from balance
    T1->>Database: conn.execute(sqlalchemy.update(accounts)<br>.where(accounts.c.id == 1)<br>.values(balance = cur_balance - book_cost(conn, item_purchased_id)))
    Note over T1, T2: Alice's Balance is $10 - $10 = $0. We lost the previous update where she added $40.
`
## Case 2: Items


## Case 3: Mods
