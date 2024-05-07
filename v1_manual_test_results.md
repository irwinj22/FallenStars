# Example workflow
Nurane, our weapons dealer, offers a set of weapons and modifiers. We take a look at the catalog, and purchase two laser pistols according to the given plan. We also buy a calibration modifier according to a separate plan. We only have one modifier, so we apply it to one of the pistols and increase the price. Finally, we update our catalog with the new items.   

1. We call POST /inventory_plan to check what to buy and execute it with POST /inventory_deliver.   
2. We then call POST /mod_plan to check our plan and execute POST /mod_deliver based on our inventory, updating any new relevant items and adding them to the catalog.   

# Testing results
1.   
Curl Statement:

Response:


2.   
Curl Statement:   

Response:


