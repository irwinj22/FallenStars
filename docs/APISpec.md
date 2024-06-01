# API Specification for FallenStars 

## 1. Items
Where all purchasing transactions between us and our items dealer occur.
1. Purchase Items

1.1 Purchase Items (POST)
**Request**
```json
[
  {
    "sku": "string", /* One of the Item SKUs listed at bottom ... */
    "type": "string", /* One of ["weapon", "armor", "other"] */
    "price": 0, /* Between 1 and 200 */
    "quantity": 0 /* Between 1 and 20 */
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
    }, 
    {
      ...
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
    }, 
    {
      ...
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
    "sku": "string", /* One of ["FIRE", "EARTH", "WATER"] */
    "type": "string", /* One of ["fire", "earth", "water"] */
    "price": 0, /* Between 1 and 200 */
    "quantity": 0, /* Between 1 and 20 */
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
    },
    {
      ...
    }
]
```

3.2 Attach Mods (POST) 
All available items that are not modified become modified until either mods or weapons run out.

**Response**
```json
"OK" /* If mods were successfully attached */
"ERROR: mods could not be attached. No items to attach to, or 0 mods entered." /* Else */
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
    "name": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
    "role": "string" /* One of Possible Roles listed below */
  },
  "checkout_items": [
    {
      "item_sku": "string", /* One of Possible Item SKUS listed below */
      "qty": 0 /* Between 1 and 20 */
    }
  ]
}
```

**Response**:
```json
"OK"
```

## 5 Recommendations
1. Get Recommendations
2. Make swap based on recommendations

5.1 POST Recommendations (POST)   
Get a recommended kit of an ideal weapon, armor, and misc. item given past purchases.

**Request**
```json
[
    {
        "budget": "integer", /* Between 1 and 2000 */ 
        "enemy_element": "string", /* One of ["FIRE", "EARTH", "WATER"] */
        "name": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "role": "string" /* One of the Possibile Roles listed at the bottom */
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

5.2 Make Swap Based on Recommendations (POST)   
The customer trades in their old items for the recommended ones

**Request**
```json
[
    {
        "weapon": "boolean", /* T or F */
        "armor": "boolean", /* T or F */
        "other": "boolean", /* T or F */
        "name": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "role": "string" /* One of Possible Roles listed at bottom */
    }
]
```
**Response**
```python 3
"OK"
```

## 6. Populate 
Populate shop with required initial inserts.

6.1 Post Populate (POST)   
Populates shop.

**Response**
```python 3
"OK"
```

Possible Item SKUS: 
'LONGSWORD'    
'FIRE_LONGSWORD'    
'EARTH_LONGSWORD'    
'WATER_LONGSWORD'    
'PISTOL'      
'FIRE_PISTOL'    
'EARTH_PISTOL'    
'WATER_PISTOL'    
'SHIELD'    
'FIRE_SHIELD'    
'EARTH_SHIELD'    
'WATER_SHIELD'    
'HELMET'    
'FIRE_HELMET'    
'EARTH_HELMET'    
'WATER_HELMET'   
'STAFF'   
'FIRE_STAFF'   
'EARTH_STAFF'   
'WATER_STAFF'   
'CHAINLINK'   
'FIRE_CHAINLINK'   
'EARTH_CHAINLINK'   
'WATER_CHAINLINK'   

Possible Roles: 
'WARRIOR'   
'SUNBLADE'   
'ASSASSIN'   
'NEXUS'   
'SHIFTER'   
'BUILDER'   
'EXPERT'   
'MAGGE'   
'SCOUT'   