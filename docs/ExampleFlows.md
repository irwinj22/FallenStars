
## Example Flows
Example Flow #1: 

Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the catalog, and purchase two laser pistols according to the given plan. We also buy a calibration modifier according to a separate plan. We only have one modifier, so we apply it to one of the pistols and increase the price. Finally, we update our catalog with the new items.

1. We call POST /inventory_plan to check what to buy and execute it with POST /inventory_deliver.
2. We then call POST /mod_plan to check our plan and execute POST /mod_deliver based on our inventory, updating any new relevant items and adding them to the catalog.


Example Flow #2:

Nicholas the Dawg wants to buy a new sword to show off to his friends. So, he asks to see the purchase catalog of our shop. He sees that we are selling 2 sharpened katanas for 70 gold and 1 longsword for 80 gold for permanent use. Nicholas wants both katanas. So, he:
1. starts by calling POST /carts to get a new cart with ID 1337.
2. Then, Nicholas calls POST /carts/1337/items/katana and passes in a quantity of 2. The shop checks if the katanas have the "sharpened" modifier before allowing Nicholas to purchase them.
3. Nicholas finally calls POST /carts/1337/checkout to buy the two sharpened katanas for 70 gold each, totalling to 140 gold.

Nicholas is excited to brag about his new katanas.


Example Flow #3:

Gabe the Babe has an internship as a part-time shepherd for the summer. So, he asks to see the rental catalog. He sees we are offering 3 concealed daggers for 50 gold each and 1 enchanted staff for 90 gold. Gabe wants the enchanted staff. So, he:
1. starts by calling POST /carts to get a new cart with ID 6666.
2. Then he calls POST /carts/6666/items/enchanted_staff and passes in a quantity of 1
3. The shop then calls POST /carts/6666/items/enchanted_staff/rental_period/100 updates the duration of the rental to be 100 ticks
4. Gabe calls POST /carts/6666/checkout to purchase the enchanted staff for 90 gold
5. Once Gabe's rent is over, the shop snatches the enchanted staff back by calling /inventory/returns
