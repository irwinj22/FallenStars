# TODO!!
Example Flow #1:

Nurane, our weapons dealer, offers a set of weapons and modifiers.

1. We call Inventory, get our current catalog, make a purchase plan, execute it, and update the inventory.
2. We then go to Modifications to check our plan and execute it based on our inventory, updating the catalog soon after.

Example Flow #2:

Nicholas the Dawg wants to buy a new sword to show off to his friends. So, he asks to see the purchase catalog of our shop. He sees that we are selling 2 sharpened katanas for 70 gold and 1 longsword for 80 gold for permanent use. Nicholas wants both katanas. So, he:
1. starts by calling POST /carts to get a new cart with ID 1337.
2. Then, Nicholas calls POST /carts/1337/items/katana and passes in a quantity of 2. The shop checks if the katanas have the "sharpened" modifier before allowing Nicholas to purchase them.
3. Nicholas finally calls POST /carts/1337/checkout to buy the two sharpened katanas for 70 gold each, totalling to 140 gold.

Nicholas is excited to brag about his new katanas.
