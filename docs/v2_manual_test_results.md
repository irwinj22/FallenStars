# Example workflow 1 
Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the weapons offerings and purchase 5 pistols. Then, we look at the mods and purchase 2 FIRE and 2 EARTH. Finally, we attach all the modifiers to weapons. 

1. Call POST/populate (ONCE) to populate datebase with necessary information (REQUIRED).
1. Call POST/items/purchase/items to purchase the pistols.
2. Call POST/mods/purchase/mods to purchase the modifications. 
3. Call POST/mods/attach/mods to attach the modifications to the weapons.

# Testing results
1. 
curl -X 'POST' \
  'http://127.0.0.1:8000/populate/' \
  -H 'accept: application/json' \
  -d ''

"OK" 

2. curl -X 'POST' \
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

3. curl -X 'POST' \
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

4. curl -X 'POST' \
  'http://127.0.0.1:8000/mods/attach/mods' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -d ''

"OK"



# Example Workflow 2 
Nicholas the Dawg wants to buy a new EARTH PISTOL to show off to his friends. So, he asks to see the purchase catalog of our shop. He sees that we are selling 1 PISTOlL, 2 FIRE_PISTOL, and 2 EARTH_PISTOL. Nicholas sees that we are offering what he wants, so he purchases the EARTH_PISTOL for 50 credits. 

1. call GET/catalog to see what is available. 
2. call POST/checkout to purchase the EARTH_PISTOL.

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
    "role": "WARRIOR"
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
Later, Nicholas the Dawg enters a new battle against an EARTH enemey and wants a recommendation as to what weapon he should buy. So, he get a recommendation of a FIRE_PISTOL (FIRE beats EARTH offensively) and then swaps his EARTH_PISTOL for a FIRE_PISTOL. 

1. call POST/recommendations/recommend to get rec. 
2. call POST/recommendations/swap to swap. 
3. call GET/catalog to see that items have been swapped.

# Testing Results 

1. curl -X 'POST' \
  'http://127.0.0.1:8000/recommendations/recommend' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer": {
    "name": "Nicholas the Dawg",
    "role": "WARRIOR"
  },
  "specs": {
    "budget": 200,
    "enemy_element": "EARTH"
  }
}'

{
  "Rec. Weapon": "FIRE_PISTOL",
  "Rec. Armor": "NA",
  "Rec. Other": "NA",
  "Total Cost": 45
}

2. curl -X 'POST' \
  'http://127.0.0.1:8000/recommendations/swap?weapon=true&armor=false&other=false' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Nicholas the Dawg",
  "role": "WARRIOR"
}'

{
  "Swapped": "EARTH_PISTOL for FIRE_PISTOL"
}

NOTE: "weapon" set to TRUE, "armor" and "other" set to FALSE


3. curl -X 'GET' \
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
    "qty": 1
  },
  {
    "sku": "EARTH_PISTOL",
    "type": "weapon",
    "mod": "EARTH",
    "price": 50,
    "qty": 2
  }
]