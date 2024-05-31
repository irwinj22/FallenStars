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
    "quantity": 10
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
    "quantity": 10,
    "compatible": [
      "weapon", "armor", "other"
    ]
  }, 
  {
    "sku": "EARTH",
    "type": "earth",
    "price": 10,
    "quantity": 10,
    "compatible": [
      "weapon", "armor", "other"
    ]
  }
]'

[
  {
    "sku": "FIRE",
    "type": "fire",
    "price": 10,
    "qty": 3
  },
  {
    "sku": "EARTH",
    "type": "earth",
    "price": 10,
    "qty": 3
  }
]

3. curl -X 'POST' \
  'http://127.0.0.1:8000/mods/attach/mods' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -d ''

"OK"



# Example Workflow 2 
Nicholas the Dawg wants to buy a new EARTH PISTOL to show off to his friends. So, he asks to see the purchase catalog of our shop. He sees that we are selling 1 PISTOlL, 2 FIRE_PISTOL, and 2 EARTH_PISTOL. Nicholas sees that we are offering what he wants, so he purchases the EARTH_PISTOL for 50 credits. 

1. call GET/catalog to see what is available. 
2. call GET/checkout to purchase the EARTH_PISTOL.

# Testing Results

1. curl -X 'GET' \
  'http://127.0.0.1:8000/catalog/' \
  -H 'accept: application/json'

[
  {
    "sku": "PISTOL",
    "type": "weapon",
    "mod": "BASIC",
    "price": 25,
    "qty": 1
  },
  {
    "sku": "FIRE_PISTOL",
    "type": "weapon",
    "mod": "FIRE",
    "price": 45,
    "qty": 2
  },
  {
    "sku": "EARTH_PISTOL",
    "type": "weapon",
    "mod": "EARTH",
    "price": 50,
    "qty": 2
  }
]

2. curl -X 'POST' \
  'http://127.0.0.1:8000/checkout/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer": {
    "name": "Nicholas the Dawg",
    "role": "Dawg"
  },
  "checkout_items": [
    {
      "item_sku": "EARTH_PISTOL",
      "qty": 1
    }
  ]
}'

“OK”

# Example Workflow 3
TODO!
Should have something to do with recommendations, once that gets done … 
