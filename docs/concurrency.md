# Concurrency Cases

## Case 1: Credits
The first case we could potentially encounter is a lost update with our store's credit total. If we did not have concurrency control protection then what could occur is we could want to take a look at our current balance and then make a purchase of a Longsword, thus deducting 50 credits from our account. However, if a customer were to make a purchase and give us credits after we found our current balance but before we updated the balance with our own purchase, then the reduced balance would be lost. Instead we use a ledgerized system where we monitor the change in credits for the shop. This way there are no updates that can overwrite each other because we make unique insert statements for each transaction, and we can sum the "change" column at any point to see how many credits we have. 


```mermaid
sequenceDiagram
    participant T1
    participant Database
    participant T2
    Note over T1, T2: Fallen Star's (account id 1) Balance is 1000 credits
    T1->>Database: Get current balance
    T1->>Database: cur_balance = conn.execute(sqlalchemy.select(accounts.c.balance).where(accounts.c.id == 1)).scalar_one();
    T2->>Database: Fallen Star's makes a pruchase of a Longsword, costing them 50 credits.
    T2->>Database: conn.execute(sqlalchemy.update(accounts).where(accounts.c.id == 1).values(balance = cur_balance - weapon_cost(conn, item_purchased_id)))
    Note over T1, T2: Fallen Star's balance is 1050 credits
    T1->>Database: Receive a payment and and add 100 credits to balance
    T1->>Database: UPDATE accounts SET balance = balance + 100 WHERE name = 'Fallen Stars'
    Note over T1, T2: Fallen Stars's Balance should be 1050 credits, but is now 1000+100 = 1000 credits due to a lost update.
```
## Case 2: Items
We could encounter another case of a lost update with our store's item inventory totals. Let's look at a specific example. If we did not have concurrency control protection then what could occur is we could want to take a look at our current total of helmets and then make a sale of a helmet to a customer, thus deducting 1 helmet from our inventory. However, if we were to make a purchase and add a helmet to our inventory after we found our current number of helmets but before we updated the helmet count with the customer's purchase, then the reduced helmet count from the shop's purchase would be lost. Instead we use a ledgerized system where we monitor the change in items for the shop. This way there are no updates that can overwrite each other because we make unique insert statements for each transaction, and we can sum the "qty_change" column at any point to see how many of a specifc item we have. 

```mermaid
sequenceDiagram
    participant T1
    participant Database
    participant T2
    Note over T1, T2: Fallen Stars (inventory id 1) has 1 helmet in inventory
    T1->>Database: Get current helmet count
    T1->>Database: cur_balance = conn.execute(sqlalchemy.select(inventory.c.helmets).where(inventory.c.id == 1)).scalar_one();
    T2->>Database: A customer makes a purchase of 1 helmet
    T2->>Database: UPDATE inventory SET helemts = helmets - 1 WHERE name = 'Fallen Stars'
    Note over T1, T2: Fallen Star's has 1 - 1 = 0 helmets in inventory
    T1->>Database: Purchase 1 helmet from our supplier
    T1->>Database: conn.execute(sqlalchemy.update(inventory).where(inventory.c.id == 1).values(helemts = helmets + 1))
    Note over T1, T2: Fallen Stars's Balance should be back to having 1 helmet in inventory, but is now 1+1 = 2 helemts due to a lost update.
```

## Case 3: Mods
