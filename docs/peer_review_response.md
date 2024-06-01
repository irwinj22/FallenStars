# Code Review Comments: Isaac Lake
1. Though we eliminated the implementation of carts, we did add a customers tables and added customer_id to items_ledger.
2. Originally, it made sense to log one item at a time because we were also trying to keep track of whether it had a mod or not (for example, could sell two items with mods and one without). However, creating entries into items_plan made that unnecessary, so now we are tracking quantity in both items_ledger and mods_ledger.
3. That file was eliminated with the redesign, but more complex SQL statements have greatly simplified our application programming.
4. JOINS are now being used in catalog (lines 18-26, for example).
5. Agreed -- credits are being tracked by adding the SUM(change) in items_ledger and mods_ledger.
6. TODO
7. TODO
8. TODO
9. TODO
10. Though that endpoint was deleted, we have reduced the number of SQL queries made throughout the entire program. 
11. That variable was eliminated with the redesign, but we have attempted to make variable naming clearer throughout the whole program. 
12. Honestly, we are not either. Regardless, that line has been eliminated and all SQL queries have been made much clearer. 

# Code Review Comments: Jeffer Ng
1. Though we are not making that query anymore, we are not making any more FULL JOINs. 
2. TODO: yes, this does need to be changed within recommendations.py.
3. Yes, no more FULL JOINs. 
4. Modifier plan has been eliminated, but there are no more connections being made within a for-loop anywhere within the code. 
5. Once again, connections within for-loops have been eliminated.
6. There are no more rental returns, but the rest of the code has been more thoroughly commented. 
7. Yes, there was a lot of overlap between the different item files. To address that we consolidated them all to one file, items, that has different types (weapon, armor, other).
8. TODO: raise errors!
9. Carts has been deleted, but total number of connections has been reduced as much as possible.
10. Repeat code within catalog has been reduced by offering only items. 
11. More comments have been made throughout the entire program. 
12. TODO: parameter binding variables have been made more specific. 

# Code Review Comments: Matthew Province
1. Syntax has been made more consistent with all-uppercase sql keywords.
2. Function header comments have been filled in. 
3. Good point -- that didn't make sense, and so was deleted.
4. TODO: this needs to be implemented (same as 2 in Jeffer Ng Code Review Comments).
5. Yes, variable names were not always informative. Variables have been renamed to make code clearer. 
6. Yes, nested conncetions have been eliminated. 
7. Yes, this was difficult to understand. Though there are no more rentals, code has been made more readable by eliminated arbitrary comparisons.
8. That function has been removed.
9. Yes, connections within loops have been deleted. 
10. Yes, that is true. However, feedback has been rejected becuase it feels like more of a personal preference. 
11. 
12. Yes, good point -- all of that has been consolidated down into items with different types (weapon, armor, other). 

# Schema/API Design Comments: Isaac Lake
1. TODO (?)
2. Good catch: this has been changed.
3. Yes -- tables have been renamed to be much more descriptive. 
4. This was a result of having so many different kinds of items. Since now only have items and mods, everything has been consolidated down into 5 tables. 
5. This was true ... table columns have been reduced as much as possible (TODO: is compatabile still necessary?).
6. Yes, we have created a file to handle the initial insertions necessary for code to run. 
7. We have changed "inventory" to "plan" in our naming. 

# Schema/API Design Comments: Jeffer Ng
1. Yes, our initial inserts have been placed into a seperate file to clean things up.
2. Yes, our naming convention was ambiguous. All names within tables have been changed to be much clearer. 
3. Yes, "log" has been changed to "ledger" the names have been appropriately lengthened. 
4. Yes, that was too vague -- it has been removed and other vague names have been changed. 
5. This is a good question -- we had forgotten to delete the "purchase_items" table, which was very confusing. 
6. Ditto for "purchase_carts".
7. Agreed -- names have been clarified throughout tables.
8. Foreign key references are now explicitly mentioned. 
9. TODO: can this be changed still? 
10. Yes, customer is a much better name and the convention has been changed to such. 
11. Yes, "logs" have been renamed as "ledgers".
12. True -- we were not using class or level, so they have been removed entirely. 

# Schema/API Design Comments: Matthew Province
1. Foreign key references have been created. 
2. This is a good idea. However, rentals are not being used anymore. 
3. TODO: set default values correctly. 
4. TODO: set constraints on what can be entered? 
5. Feedback has been rejected because we do not know what it means. 
6. Yes, the units were ambiguous .. 
TODO: make it clear what the user should input for certain things, such as class 
--> this can come in the API spec, then be reinforced in the error catching .. 
7. Similar functions have been consolidated. 
8. Though that endpoint has been eliminated, others have been consolidated, such as buying items and mods. 
9. Yes, this was a good idea -- all item types have been combined. 
10. TODO: constraints for possible values should be listed in the SPEC.
11. TODO: more constriants stuff.
12. Duplication and unnecessary endpoints have been eliminated. 

# Product Ideas: Isaac Lake
1. A good idea, but the feedback has been rejected because we feel it would take away from the core of our business (buying and selling weapons).
2. Yes, this is a great idea that we were hoping to implement, but did not have enough time for. 

# Product Ideas: Jeffer Ng
1. This is a good idea, but the feedback has been rejected because we feel that it would be too difficult to implement within our timeframe. 
2. This is also a good idea. It has been implemented, in part, with our "swap" endpoint. 

# Product Ideas: Matthew Province. 
1. No, the endpoint was not fully implemented at the time. However, we have moved away from rentals because we felt that recommendations was a better complex endpoint. 
2. This is a good idea. However, the feedback has been rejected because we are not offering rentals anymore. 

TODO: all of the Test Results ... 
