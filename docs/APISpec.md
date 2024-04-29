# API Specification for FallenStars 

## 1. Customer Purchases

API calls are made in this sequence during customer purchase: 
1. Get Purchase Catalog
2. New Cart
3. Add Item to Cart (Repeatable)
4. Add Modification Plan (Repeatable)
5. Checkout

1.1 Get Purchase Catalog (GET)   
Retrives catalog of purchasable items. 

**Response**:

```json
[
    {
        "sku": "string", 
        "name": "string",
        "quantity": "integer",
        "price": "integer", 
        "modifiers": ["s", "t", "r", "..."]
    }
]
```

1.2 New Cart (POST)   
Creates new cart for specified customer. 

**Request**:

```json
{
  "customer_name": "string",
  "character_class": "string",
  "level": "number"
}
```

**Response**:

```json
{
  "cart_id": "string"
}
```

1.3 Add Item to Cart (POST)    
Updates quantity of item in cart.

**Request**:

```json
{
  "quantity": "integer"
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

1.4 Add Modification Plan (POST)    
Add modification(s) to specific item(s) within cart.

**Request**:

```json
{
  "modification_plan": ["s", "t", "r", "..."]
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

1.5 Checkout (POST)   
Checkout process for cart. 

**Response**:

```json
{
    "items_and_amount_bought": ["s", "t", "r", "..."]
    "credits_paid": "integer"
}
```

## 2. Customer Rentals   
API calls are made in this sequence during customer rentals:
1. Get Rental Catalog
2. New Cart
3. Add Item to Cart (Repeatable)
4. Rental duration (Repeatable)
5. Checkout
6. Return

2.1 Get Rental Catalog (GET)   
Retrives catalog of rentable items. 

**Response**:

```json
[
    {
        "sku": "string", 
        "name": "string",
        "quantity": "integer",
        "price": "integer", 
        "modifiers": ["s", "t", "r", "..."]
        "expiry_time": "integer"
    }
]
```

2.2 New Cart (POST)   
Creates new cart for specified customer. 

**Request**:

```json
{
  "customer_name": "string",
  "character_class": "string",
  "level": "number"
}
```

**Response**:

```json
{
  "cart_id": "string"
}
```

2.3 Add Item to Cart (POST)   
Updates quantity of item in cart. 

**Request**:

```json
{
  "quantity": "integer"
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

2.4 Rental Duration (POST)   
Updates duration of rental for specified item in cart. 

**Request**:

```json
{
  "expiry_time": "integer"
}
```

**Response**:

```json
{
    "success": "boolean"
}
```



2.5 Checkout (POST)   
Checkout process for cart.

**Response**:

```json
{
    "items_and_amount_bought": ["s", "t", "r", "..."]
    "credits_paid": "integer"
}
```

2.6 Return (GET)
Item is returned after a certain number of ticks.

**Response**:

```json
{
    "success": "boolean"
}
```

## 3. Customer Returns
API calls are made in this sequence during customer returns:
1. Get Customer Catalog
2. Evaluate Condition
3. Update Inventory
4. Issue Refund

3.1 Get Cusomter Catalog (GET)   
Customers presents list of items (and their conditions) to be evaluated for possibility of return. 

**Response**:

```json
{
    "to_be_evaluated": [["s", "condition"], ["t", "condition"], ["r", "condition"], ["..."], "condition"]
}
```

3.2 Evaluate Condition ()   
Condition of each item in customer catalogue is evaluated. 

**Request**:

```json
{
    "to_be_evaluated": [["s", "condition"], ["t", "condition"], ["r", "condition"], "..."]
}
```

**Response**:

```json
{
    "success": [b, o, o, l, ...]
}
```

3.3. Update Inventory (POST)   
Inventory updated with all items that had returnable condition

**Response**:

```json
{
    "good_condition": ["s", "t", "r", ...]
}
```

3.4 Issue Refund (POST)   
Refund issued to customer

**Request**:

```json
{
    "refund_amount": "integer"
}
```

**Response**:

```json
{
    "success": [b, o, o, l, ...]
}
```

##  4. Inventory
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

## 5. Admin
1. Self-audit
2. Reset

5.1 Self-audit (GET)
Return database numbers for easy readability and to test expected values.

5.2 Reset ()
Set all values to default, clear out all customer info.

## 6. Modifications
1. Modification Plan
2. Modification Deliverance

6.1 Modification Plan (POST)
Collect catalog for modifications and add attributes as needed according to the given plan.

6.2 Modification Deliverance (POST)
Add modifications to current catalog items where applicable. 

## 7. Ability Verifier
1. Group Customers
2. Deliver Group

7.1 Group Customers (POST)
Create groups by group plan, splitting customers by class and level.

7.2 Deliver Group (Post)
Pass in customer JSON list and pass out array of arrays.

## 8 Catalog 
1. Filter
2. Sort 
3. Get

8.1 Filter (GET)
Filter items that are too old to sell to reduce returns.

8.2 Sort (GET)
Move items into one of three groups: weaponry, armor, and trinket.

8.3 Get (GET)
Returns the updated catalog for other endpoints.
