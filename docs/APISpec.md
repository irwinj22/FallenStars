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
    "checkout_time": "integer"
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
    "to_be_evaluated": [["s", "condition"], ["t", "condition"], ["r", "condition"], ["...", "condition"]]
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
2. Create Weapon Purchase Plan
3. Create Armor Purchase Plan
4. Create Item Purchase Plan
5. Execute Weapon Purchases
6. Execute Misc Purchases

4.1 Get Complete Inventory (GET)   
Complete Inventory of shop is retrieved

**Response**:

```json
{
    "num_weaponry": "integer",
    "num_armor": "integer",
    "num_items": "integer",
    "num_rental": "integer",
    "credits": "integer"
}
```

4.2 Create Weapon Purchase Plan (POST)   
Purchase plan is created based on current inventory.

**Request**
```json
[
    {
        "sku": "string",
        "name": "string",
        "type": "string",
        "damage": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```
**Response**
```json
[
    {
        "sku": "string", /*Needs to match a sku in the request catalog */
        "quantity": "integer" /*Needs to be equal or less than in request catalog */
    }
]
```

4.3 Create Armor Purchase Plan (POST)
Purchase plan is created based on current inventory. Since weapons have an additional parameter, they are separate from armor and items.
**Request**
```json
[
    {
        "sku": "string",
        "name": "string",
        "type": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```
**Response**
```json
[
    {
        "sku": "string", /*Needs to match a sku in the request catalog */
        "quantity": "integer" /*Needs to be equal or less than in request catalog */
    }
]
```

4.4 Item Purchase Plans (POST)
**Request**
```json
[
    {
        "sku": "string",
        "name": "string",
        "type": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```
**Response**
```json
[
    {
        "sku": "string", /*Needs to match a sku in the request catalog */
        "quantity": "integer" /*Needs to be equal or less than in request catalog */
    }
]
```

4.5 Execute Weapon Purchase (POST)   
Purchase plan executed, newly purchased items are returned
**Request** 
```json
[
    {
        "sku": "string", /*All lines consisting of items that passed purchase plan */
        "name": "string",
        "type": "string",
        "damage": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```

4.6 Execute Misc. Purchase (POST)
Purchase plan executed, newly purchased items are returned
**Request** 
```json
[
    {
        "sku": "string", /*All lines consisting of items that passed purchase plan */
        "name": "string",
        "type": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```

## 5. Admin
1. Self-audit
2. Reset

5.1 Self-audit (GET)
Return database numbers for easy readability and to test expected values.
**Response**
```json
{
    "num_weapons": "integer",
    "num_armor": "integer",
    "num_items": "integer",
    "num_mods": "integer",
    "credits": "integer"
}
```

5.2 Reset ()
Set all values to default, clear out all customer info.

## 6. Modifications
1. Modification Plan
2. Modification Deliverance

6.1 Modification Plan (POST)
Collect catalog for modifications and add attributes as needed according to the given plan.
**Request**
```json
[
    {
        "sku": "string",
        "name": "string",
        "compatibility": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```
**Response**
```json
[
    {
        "sku": "string", /*Needs to match a sku in the request catalog */
        "quantity": "integer" /*Needs to be equal or less than in request catalog */
    }
]
```

6.2 Modification Deliverance (POST)
Add modifications to current catalog items where applicable. 
**Request**
```json
[
    {
        "sku": "string",
        "name": "string",
        "type": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```

## 7. Ability Verifier
1. Group Customers

7.1 Group Customers (POST)
Create groups by group plan, splitting customers by class and level.
**Response**
```json
[
    {
        "name": "string",
        "class": "string",
        "level": "string"
    }
]
```

## 8 Catalog 
1. Filter 
2. Get Weapons
3. Get Armor
4. Get Items

8.1 Filter (POST)
Filter items that are too old to sell to reduce returns.

8.2 Get Weapons (GET)
Returns the updated weapons catalog for other endpoints.
**Request** 
```json
[
    {
        "sku": "string",
        "name": "string",
        "type": "string",
        "damage": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```

8.3 Get Armor (GET)
Returns the updated armor catalog for other endpoints.
**Request** 
```json
[
    {
        "sku": "string", 
        "name": "string",
        "type": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```

8.4 Get Items (GET)
Returns the updated items catalog for other endpoints.
**Request** 
```json
[
    {
        "sku": "string", 
        "name": "string",
        "type": "string",
        "price": "integer",
        "quantity": "integer"
    }
]
```

## 9 Recommendations
1. Get Recommendations
2. Make swap based on recommendations

9.1 Get Recommendations (GET)   
Get a recommended kit of an ideal weapon, armor, and misc. item

**Request**
```json
[
    {
        "budget": "integer",
        "enemy_element": "string",
        "name": "string",
        "role": "string"
    }
]
```

**Response**:

```json
{
    "Rec. Weapon": "string",
    "Rec. Armor": "string",
    "Rec. Other": "string",
    "total_cost": "integer"
}
```

9.2 Make Swap Based on Recommendations (POST)   
The customer trades in their old items for the recommended ones

**Request**
```json
[
    {
        "weapon": "boolean",
        "armor": "boolean",
        "other": "boolean",
        "name": "string",
        "role": "string"
    }
]
```
**Response**
```python 3
"OK"
```