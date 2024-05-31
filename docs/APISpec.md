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