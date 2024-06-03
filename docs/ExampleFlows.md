
# Example Flows

## Example Flow 1 
Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the weapons offerings and purchase 5 pistols. Then, we look at the mods and purchase 2 FIRE and 2 EARTH. Finally, we attach all the modifiers to weapons. 

1. Call POST/items/purchase/items to purchase the pistols.
2. Call POST/mods/purchase/mods to purchase the modifications. 
3. Call POST/mods/attach/mods to attach the modifications to the weapons.


## Example Flow 2
Nicholas the Dawg wants to buy a new EARTH PISTOL to show off to his friends. So, he asks to see the purchase catalog of our shop. He sees that we are selling 1 PISTOlL, 2 FIRE_PISTOL, and 2 EARTH_PISTOL. Nicholas sees that we are offering what he wants, so he purchases the EARTH_PISTOL for 50 credits. 

1. call GET/catalog to see what is available. 
2. call POST/checkout to purchase the EARTH_PISTOL.


# Example Flow 3
Later, Nicholas the Dawg enters a new battle against an EARTH enemey and wants a recommendation as to what weapon he should buy. So, he get a recommendation of a FIRE_PISTOL and then swaps his EARTH_PISTOL for a FIRE_PISTOL. 

1. call POST/recommendations/recommend to get rec. 
2. call POST/recommendations/swap to swap.
