# Example workflow 1 
Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the catalog, and purchase two laser pistols according to the given plan. We also buy a calibration modifier according to a separate plan. We only have one modifier, so we apply it to one of the pistols and increase the price.  

1. call POST /items/weapon_plan and determine what weapons to buy 
2. call POST /items/deliver_weapon to add weapon ledger entry
3. call POST /modifier/plan and determine what modifiers to buy
4. call POST /modifier/deliver to add modifier ledger entry    


# Testing results
1. curl -X 'POST' \
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

2. curl -X 'POST' \
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

3. curl -X 'POST' \
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

4. curl -X 'POST' \
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

# Example Workflow 2 
Nicholas the Dawg wants to buy a new sword to show off to his friends. So, he asks to see the purchase catalog of our shop. He sees that we are selling 2 sharpened katanas for 70 credits and 1 longsword for 80 credits for permanent use. Nicholas wants both katanas.

1. call GET/catalog to see what is available. 
2. call POST/carts to create a new cart.
3. call POST /carts/items/ to add two katanas to cart. 
4. call POST /carts/checkout to purchase.

# Testing Results
1.  
curl -X 'GET' \
  'http://127.0.0.1:8000/catalog/' \
  -H 'accept: application/json'   
[
  {
    "thing_id": 3,
    "sku": "LONGSWORD",
    "name": "long sword",
    "type": "melee",
    "damage": "heavy",
    "modifier": null,
    "price": 80,
    "quantity": 1,
    "rental": false
  },
  {
    "thing_id": 2,
    "sku": "KATANA",
    "name": "katana",
    "type": "melee",
    "damage": "medium",
    "modifier": null,
    "price": 35,
    "quantity": 1,
    "rental": false
  }
]   


2. 
curl -X 'POST' \
  'http://127.0.0.1:8000/carts/' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer_name": "Nicholas the Dawg",
  "character_class": "Canine",
  "level": 9
}'  
{
  "cart_id": 7
}

3. 
curl -X 'POST' \
  'http://127.0.0.1:8000/carts/7/items/{item_sku}?type=melee&type_id=2' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '{
  "quantity": 2
}'     
"OK"

4. 
curl -X 'POST' \
  'http://127.0.0.1:8000/carts/7/checkout' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -d ''     
{
  "total_purchases": 2,
  "total_credits_paid": 70
}

# Example Workflow 3
Gabe the Babe has an internship as a part-time shepherd for the summer. So, he asks to see the rental catalog. He sees we are offering 1 enchanted staff for 90 credits. Gabe wants the enchanted staff.

1. call GET/catalog to see what's available. 
2. call POST/carts to create new cart (id 9).
3. call POST/carts/9/items/enchanted_staff, pass in a quantity of 1.
4. call POST/carts/6666/checkout to rent the enchanted staff for 90 credits.


1.
curl -X 'GET' \
  'http://127.0.0.1:8000/catalog/' \
  -H 'accept: application/json'   
[
  {
    "thing_id": 3,
    "sku": "LONGSWORD",
    "name": "long sword",
    "type": "melee",
    "damage": "heavy",
    "modifier": null,
    "price": 80,
    "quantity": 1,
    "rental": false
  },
  {
    "thing_id": 2,
    "sku": "KATANA",
    "name": "katana",
    "type": "melee",
    "damage": "medium",
    "modifier": null,
    "price": 35,
    "quantity": 3,
    "rental": false
  },
  {
    "thing_id": 1,
    "sku": "ENCHANTED_STAFF",
    "name": "enchanted staff",
    "type": "support",
    "modifier": null,
    "price": 80,
    "quantity": 1,
    "rental": true
  }
]    

2. 
curl -X 'POST' \
  'http://127.0.0.1:8000/carts/' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '{
  "customer_name": "Gabe the Babe",
  "character_class": "Gabes",
  "level": 10
}'
{
  "cart_id": 9
}    

3. 
curl -X 'POST' \
  'http://127.0.0.1:8000/carts/9/items/{item_sku}?type=support&type_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -H 'Content-Type: application/json' \
  -d '{
  "quantity": 1
}'    
"OK"    
    
4.    
curl -X 'POST' \
  'http://127.0.0.1:8000/carts/9/checkout' \
  -H 'accept: application/json' \
  -H 'access_token: armory' \
  -d ''   
{
  "total_purchases": 1,
  "total_credits_paid": 80
}
