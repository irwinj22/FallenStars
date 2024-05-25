# Example workflow
Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the catalog, and purchase two laser pistols according to the given plan. We also buy a calibration modifier according to a separate plan. We only have one modifier, so we apply it to one of the pistols and increase the price. Finally, we update our catalog with the new items.   

1. call POST /items/weapon_plan and determine what weapons to buy 
2. call POST /items/deliver_weapon to add weapon ledger entry
3. call POST /modifier/plan and determine what modifiers to buy
4. call POST /modifier/deliver to add modifier ledger entry    


# Testing results
1.    
curl -X 'POST' \
  'http://127.0.0.1:8000/items/weapon_plan' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "sku": "LASER_PISTOL",
    "type": "medium",
    "damage": "big",
    "price": 10,
    "quantity": 10
  }
]'   
[
  {
    "sku": "LASER_PISTOL",
    "quantity": 2
  }
]    

2.    
curl -X 'POST' \
  'http://127.0.0.1:8000/items/deliver_weapon?order_id=2' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "sku": "LASER_PISTOL",
    "type": "medium",
    "damage": "big",
    "price": 10,
    "quantity": 10
  }
]
'     
"OK"    

3.     
curl -X 'POST' \
  'http://127.0.0.1:8000/modifier/plan' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "sku": "CALIBRATION",
    "type": "small",
    "damage": "heavy",
    "price": 20,
    "quantity": 4
  }
]'
[
  {
    "sku": "CALIBRATION",
    "quantity": 1
  }
]
4.    
curl -X 'POST' \
  'http://127.0.0.1:8000/modifier/deliver/2' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "sku": "CALIBRATION",
    "quantity": 1
  }
]'   
"OK"


