## API Specification for FallenStars 

# 1. Customer Purchases

API calls are made in this sequence during customer purchase: 
1. Get Purchase Catalog
2. New Cart
3. Add Item to Cart (Repeatable)
4. Add Modification Plan (Repeatable)
5. Ability Verifier
6. Checkout

1.1 Get Purchase Catalog (GET)
Retrives catalog of purchasable items. 

1.2 New Cart (POST)
Creates new cart for specified customer. 

1.3 Add Item to Cart (POST)
Updates quantity of item in cart. 

1.4 Add Modification Plan (POST)
Add modification(s) to specific item(s) within cart.

1.5 Ability Verifier (POST)
Presented abilites of purchaser are verified. 
(Some items are only purchasable by high-level customers)

1.6 Checkout (POST)
Checkout process for cart. 

# 2. Customer Rentals
API calls are made in this sequence during customer rentals:
1. Get Rental Catalog
2. New Cart
3. Add Item to Cart (Repeatable)
4. Rental duration (Repeatable)
5. Ability Verifier
6. Checkout

1.1 Get Rental Catalog (GET)
Retrives catalog of rentable items. 

1.2 New Cart (POST)
Creates new cart for specified customer. 

1.3 Add Item to Cart (POST)
Updates quantity of item in cart. 

1.4 Rental Duration (POST)
Updates duration of rental for specified item in cart. 

1.5 Ability Verifier (POST)
Presented abilites of renter are verified. 
(Some items are only rentable by high-level customers)

1.6 Checkout (POST)
Checkout process for cart.

# 3. Customer Returns
API calls are made in this sequence during customer returns:
1. Get Customer Catalog
2. Evaluate Condition
3. Update Inventory
4. Issue Refund

3.1 Get Cusomter Catalog (GET)
Customers presents list of items (and their conditions) to be evaluated for possibility of return. 

3.2 Evaluate Condition ()
Condition of each item in customer catalogue is evaluated. 

3.3. Update Inventory (POST)
Inventory updated with all items that had returnable condition

3.4 Issue Refund (POST)
Refund issued to customer

# 4. Inventory
API calls are made in this sequence during Inventory: 
1. Get Complete Inventory
2. Create Purchase Plan
3. Execute Purchase Plan
4. Update Inventory

4.1 Get Complete Inventory (GET)
Complete Inventory of shop is retrieved

4.2 Create Purchase Plan (POST)
Purchase plan is created based on current inventory

4.3 Execute Purchase Plan (POST)
Purchase plan executed, newly purchased items are returned

4.4. Update Inventory (POST)
Upon return of newly purchased items, inventory is updated. 

# 5. Admin
# TODO!!
Self-audit (?)

