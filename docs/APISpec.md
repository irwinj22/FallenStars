# API Specification for FallenStars 

## 1. Items
Where all purchasing transactions happen between us and our items dealer.
1. Purchase Items

1.1 Purchase Items (POST)
**Request**
```json
[
  {
    "sku": "string",
    "type": "string",
    "price": 0,
    "quantity": 0
  }
]
```

**Response**
```json
[
    {
        "qty": "int", 
        "item_id": "int",
        "item_sku": "string", 
        "credit_change": "int"
    }
]
```

## 2. Catalog 
Get all items in the shop.

2.1 Get Catalog (GET)   
Retrives catalog of rentable items. 

**Response**
```json
[
    {
        "sku" : "string", 
        "type" : "string",
        "mod" : "string",
        "price" : "int",
        "qty" : "int"
    }      
]
```

## 3. Mods
API calls are made in this sequence to purchase and modify items:
1. Purchase Mods
2. Attach Mods

3.1 Purchase Mods (POST) 
Mods are purchased based off the current catalog available for the shop to buy.

**Request**
```json
[
  {
    "sku": "string",
    "type": "string",
    "price": 0,
    "quantity": 0,
    "compatible": [
      "string"
    ]
  }
]
```

**Response**
```json
[
    {
        "qty": "int", 
        "mod_id": "int",
        "mod_sku": "string", 
        "credit_change": "int"
    }
]
```

3.2 Attach Mods (POST) 
All available items that are not modified become modified until either mods or weapons run out.

**Response**
```json
"OK" /*if mods were successfully attached.*/
"ERROR: mods could not be attached. No items to attach to, or 0 mods entered." /*else.*/
```

##  4. Checkout
API calls are made in this sequence during Checkout: 
1. Checkout

4.1 Checkout (POST)
A customer makes a purchase and logs their relevant information.

**Request**
```json
{
  "customer": {
    "name": "string",
    "role": "string"
  },
  "checkout_items": [
    {
      "item_sku": "string",
      "qty": 0
    }
  ]
}
```

**Response**:
```json
"OK"
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


