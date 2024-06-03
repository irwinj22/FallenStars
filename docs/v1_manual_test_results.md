# Example workflow 1 
Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the weapons offerings and purchase 5 pistols. Then, we look at the mods and purchase 2 FIRE and 2 EARTH. Finally, we attach all the modifiers to weapons. 

1. Call POST/items/purchase/items to purchase the pistols.
2. Call POST/mods/purchase/mods to purchase the modifications. 
3. Call POST/mods/attach/mods to attach the modifications to the weapons.

# Testing results
1. curl -X 'POST' \
  'http://127.0.0.1:8000/items/purchase/items' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "sku": "PISTOL",
    "type": "weapon",
    "price": 20,
    "quantity": 5
  }
]'

[
  {
    "sku": "PISTOL",
    "type": "weapon",
    "price": 20,
    "qty": 5
  }
]

2. curl -X 'POST' \
  'http://127.0.0.1:8000/mods/purchase/mods' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "sku": "FIRE",
    "type": "fire",
    "price": 10,
    "quantity": 2
  }, 
  {
    "sku": "EARTH",
    "type": "earth",
    "price": 10,
    "quantity": 2
  }
]'

[
  {
    "sku": "FIRE",
    "type": "fire",
    "price": 10,
    "qty": 2
  },
  {
    "sku": "EARTH",
    "type": "earth",
    "price": 10,
    "qty": 2
  }
]

3. curl -X 'POST' \
  'http://127.0.0.1:8000/mods/attach/mods' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -d ''

"OK"
