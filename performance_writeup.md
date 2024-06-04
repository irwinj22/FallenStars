Fake Data Modeling

python file that creates fake rows: populate.py

We decided to distribute the million rows by having 200,000 rows in “customers,” 400,000 entries in the “items_ledger,” and 400,000 entries in the “mods_ledger.” We chose these values because we wanted to simulate item and modification purchases from our shopkeeper and transactions from our customers. Also, while 200,000 unique customers seems like a lot, we have a lot of items to sell so with this set of fake data it is logical to have a lot of people show up to our shop. Furthermore, we did not add any rows to “items_plan” or “mods_plan” because our code never adds to the list of possible items that we can sell and the modifications that we apply to those items.



Performance Results of Hitting Endpoints

Catalog.py: 203.768ms  

Checkout.py: 13.076 ms  
Items.py: 129.646 ms  
Mods.py: 185.044 ms  
Recommendations.py: 288.828 ms  



Performance Tuning

 - catalog.py:

    SELECT items_plan.id AS "item_id", items_plan.sku AS "item_sku", items_plan.type AS "type",
           mods_plan.id AS "mod_id", mods_plan.sku AS "mod_sku", items_plan.price AS "price", 
           SUM(items_ledger.qty_change) AS "qty" 
    FROM items_plan
    JOIN items_ledger ON . = items_plan.id 
    JOIN mods_plan ON mods_plan.id = items_plan.mod_id
    GROUP BY items_plan.id, items_plan.sku, items_plan.type, mods_plan.id, mods_plan.sku
    HAVING SUM(items_ledger.qty_change) > 0

    | QUERY PLAN                                                                                                                           |
    | ------------------------------------------------------------------------------------------------------------------------------------ |
    | HashAggregate  (cost=12992.35..13247.35 rows=6800 width=70) (actual time=180.874..180.962 rows=24 loops=1)                           |
    |   Group Key: items_plan.id, mods_plan.id                                                                                             |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                                         |
    |   Batches: 1  Memory Usage: 793kB                                                                                                    |
    |   ->  Hash Join  (cost=30.66..9992.34 rows=400001 width=66) (actual time=0.035..132.910 rows=400001 loops=1)                         |
    |         Hash Cond: (items_plan.mod_id = mods_plan.id)                                                                                |
    |         ->  Hash Join  (cost=1.54..8907.97 rows=400001 width=34) (actual time=0.026..88.295 rows=400001 loops=1)                     |
    |               Hash Cond: (items_ledger.item_id = items_plan.id)                                                                      |
    |               ->  Seq Scan on items_ledger  (cost=0.00..7671.01 rows=400001 width=8) (actual time=0.009..24.255 rows=400001 loops=1) |
    |               ->  Hash  (cost=1.24..1.24 rows=24 width=30) (actual time=0.010..0.011 rows=24 loops=1)                                |
    |                     Buckets: 1024  Batches: 1  Memory Usage: 10kB                                                                    |
    |                     ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=30) (actual time=0.002..0.004 rows=24 loops=1)        |
    |         ->  Hash  (cost=18.50..18.50 rows=850 width=36) (actual time=0.004..0.004 rows=4 loops=1)                                    |
    |               Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                           |
    |               ->  Seq Scan on mods_plan  (cost=0.00..18.50 rows=850 width=36) (actual time=0.001..0.002 rows=4 loops=1)              |
    | Planning Time: 0.283 ms                                                                                                              |
    | Execution Time: 181.306 ms                                                                                                           |

    This information tells me that a long part of the query was executing the aggregate function. So, indexes based on GROUP BY may be helpful.

        CREATE INDEX items_plan_id_sku_type_idx ON items_plan (id, sku, type)
        CREATE INDEX mods_plan_id_sku_idx ON mods_plan(id, sku)

    | QUERY PLAN                                                                                                                                                      |
    | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | Finalize GroupAggregate  (cost=9010.25..9035.29 rows=32 width=70) (actual time=74.631..79.676 rows=24 loops=1)                                                  |
    |   Group Key: items_plan.id, mods_plan.id                                                                                                                        |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                                                                    |
    |   ->  Gather Merge  (cost=9010.25..9032.65 rows=192 width=70) (actual time=74.626..79.661 rows=72 loops=1)                                                      |
    |         Workers Planned: 2                                                                                                                                      |
    |         Workers Launched: 2                                                                                                                                     |
    |         ->  Sort  (cost=8010.22..8010.46 rows=96 width=70) (actual time=72.194..72.198 rows=24 loops=3)                                                         |
    |               Sort Key: items_plan.id, mods_plan.id                                                                                                             |
    |               Sort Method: quicksort  Memory: 27kB                                                                                                              |
    |               Worker 0:  Sort Method: quicksort  Memory: 27kB                                                                                                   |
    |               Worker 1:  Sort Method: quicksort  Memory: 27kB                                                                                                   |
    |               ->  Partial HashAggregate  (cost=8006.10..8007.06 rows=96 width=70) (actual time=72.162..72.168 rows=24 loops=3)                                  |
    |                     Group Key: items_plan.id, mods_plan.id                                                                                                      |
    |                     Batches: 1  Memory Usage: 24kB                                                                                                              |
    |                     Worker 0:  Batches: 1  Memory Usage: 24kB                                                                                                   |
    |                     Worker 1:  Batches: 1  Memory Usage: 24kB                                                                                                   |
    |                     ->  Hash Join  (cost=2.63..6756.10 rows=166667 width=66) (actual time=0.043..54.359 rows=133334 loops=3)                                    |
    |                           Hash Cond: (items_plan.mod_id = mods_plan.id)                                                                                         |
    |                           ->  Hash Join  (cost=1.54..5853.96 rows=166667 width=34) (actual time=0.026..35.197 rows=133334 loops=3)                              |
    |                                 Hash Cond: (items_ledger.item_id = items_plan.id)                                                                               |
    |                                 ->  Parallel Seq Scan on items_ledger  (cost=0.00..5337.67 rows=166667 width=8) (actual time=0.006..11.241 rows=133334 loops=3) |
    |                                 ->  Hash  (cost=1.24..1.24 rows=24 width=30) (actual time=0.012..0.013 rows=24 loops=3)                                         |
    |                                       Buckets: 1024  Batches: 1  Memory Usage: 10kB                                                                             |
    |                                       ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=30) (actual time=0.005..0.007 rows=24 loops=3)                 |
    |                           ->  Hash  (cost=1.04..1.04 rows=4 width=36) (actual time=0.012..0.012 rows=4 loops=3)                                                 |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                    |
    |                                 ->  Seq Scan on mods_plan  (cost=0.00..1.04 rows=4 width=36) (actual time=0.007..0.007 rows=4 loops=3)                          |
    | Planning Time: 0.589 ms                                                                                                                                         |
    | Execution Time: 79.825 ms                                                                                                                                       |

    These indexes had negligible effects on the query, unlike how I had assumed. This might be because the time that each column is considered once is already very small. 

        CREATE INDEX items_ledger_item_id_idx ON items_ledger (item_id)

    | QUERY PLAN                                                                                                                                                      |
    | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | Finalize GroupAggregate  (cost=9010.25..9035.29 rows=32 width=70) (actual time=72.697..75.214 rows=24 loops=1)                                                  |
    |   Group Key: items_plan.id, mods_plan.id                                                                                                                        |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                                                                    |
    |   ->  Gather Merge  (cost=9010.25..9032.65 rows=192 width=70) (actual time=72.688..75.193 rows=72 loops=1)                                                      |
    |         Workers Planned: 2                                                                                                                                      |
    |         Workers Launched: 2                                                                                                                                     |
    |         ->  Sort  (cost=8010.22..8010.46 rows=96 width=70) (actual time=70.314..70.318 rows=24 loops=3)                                                         |
    |               Sort Key: items_plan.id, mods_plan.id                                                                                                             |
    |               Sort Method: quicksort  Memory: 27kB                                                                                                              |
    |               Worker 0:  Sort Method: quicksort  Memory: 27kB                                                                                                   |
    |               Worker 1:  Sort Method: quicksort  Memory: 27kB                                                                                                   |
    |               ->  Partial HashAggregate  (cost=8006.10..8007.06 rows=96 width=70) (actual time=70.285..70.293 rows=24 loops=3)                                  |
    |                     Group Key: items_plan.id, mods_plan.id                                                                                                      |
    |                     Batches: 1  Memory Usage: 24kB                                                                                                              |
    |                     Worker 0:  Batches: 1  Memory Usage: 24kB                                                                                                   |
    |                     Worker 1:  Batches: 1  Memory Usage: 24kB                                                                                                   |
    |                     ->  Hash Join  (cost=2.63..6756.10 rows=166667 width=66) (actual time=0.077..53.095 rows=133334 loops=3)                                    |
    |                           Hash Cond: (items_plan.mod_id = mods_plan.id)                                                                                         |
    |                           ->  Hash Join  (cost=1.54..5853.96 rows=166667 width=34) (actual time=0.044..34.653 rows=133334 loops=3)                              |
    |                                 Hash Cond: (items_ledger.item_id = items_plan.id)                                                                               |
    |                                 ->  Parallel Seq Scan on items_ledger  (cost=0.00..5337.67 rows=166667 width=8) (actual time=0.010..11.368 rows=133334 loops=3) |
    |                                 ->  Hash  (cost=1.24..1.24 rows=24 width=30) (actual time=0.025..0.025 rows=24 loops=3)                                         |
    |                                       Buckets: 1024  Batches: 1  Memory Usage: 10kB                                                                             |
    |                                       ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=30) (actual time=0.009..0.012 rows=24 loops=3)                 |
    |                           ->  Hash  (cost=1.04..1.04 rows=4 width=36) (actual time=0.023..0.024 rows=4 loops=3)                                                 |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                    |
    |                                 ->  Seq Scan on mods_plan  (cost=0.00..1.04 rows=4 width=36) (actual time=0.009..0.011 rows=4 loops=3)                          |
    | Planning Time: 0.919 ms                                                                                                                                         |
    | Execution Time: 75.332 ms                                                                                                                                       |

    This is the same issue as before. We can try an index on qty_change because the query relies on that as well.

        CREATE INDEX items_ledger_qty_change_idx ON items_ledger (qty_change)

    | QUERY PLAN                                                                                                                                                      |
    | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | Finalize GroupAggregate  (cost=9010.25..9035.29 rows=32 width=70) (actual time=69.408..73.566 rows=24 loops=1)                                                  |
    |   Group Key: items_plan.id, mods_plan.id                                                                                                                        |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                                                                    |
    |   ->  Gather Merge  (cost=9010.25..9032.65 rows=192 width=70) (actual time=69.402..73.550 rows=72 loops=1)                                                      |
    |         Workers Planned: 2                                                                                                                                      |
    |         Workers Launched: 2                                                                                                                                     |
    |         ->  Sort  (cost=8010.22..8010.46 rows=96 width=70) (actual time=66.839..66.842 rows=24 loops=3)                                                         |
    |               Sort Key: items_plan.id, mods_plan.id                                                                                                             |
    |               Sort Method: quicksort  Memory: 27kB                                                                                                              |
    |               Worker 0:  Sort Method: quicksort  Memory: 27kB                                                                                                   |
    |               Worker 1:  Sort Method: quicksort  Memory: 27kB                                                                                                   |
    |               ->  Partial HashAggregate  (cost=8006.10..8007.06 rows=96 width=70) (actual time=66.807..66.813 rows=24 loops=3)                                  |
    |                     Group Key: items_plan.id, mods_plan.id                                                                                                      |
    |                     Batches: 1  Memory Usage: 24kB                                                                                                              |
    |                     Worker 0:  Batches: 1  Memory Usage: 24kB                                                                                                   |
    |                     Worker 1:  Batches: 1  Memory Usage: 24kB                                                                                                   |
    |                     ->  Hash Join  (cost=2.63..6756.10 rows=166667 width=66) (actual time=0.068..50.198 rows=133334 loops=3)                                    |
    |                           Hash Cond: (items_plan.mod_id = mods_plan.id)                                                                                         |
    |                           ->  Hash Join  (cost=1.54..5853.96 rows=166667 width=34) (actual time=0.039..32.306 rows=133334 loops=3)                              |
    |                                 Hash Cond: (items_ledger.item_id = items_plan.id)                                                                               |
    |                                 ->  Parallel Seq Scan on items_ledger  (cost=0.00..5337.67 rows=166667 width=8) (actual time=0.008..10.076 rows=133334 loops=3) |
    |                                 ->  Hash  (cost=1.24..1.24 rows=24 width=30) (actual time=0.019..0.019 rows=24 loops=3)                                         |
    |                                       Buckets: 1024  Batches: 1  Memory Usage: 10kB                                                                             |
    |                                       ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=30) (actual time=0.006..0.013 rows=24 loops=3)                 |
    |                           ->  Hash  (cost=1.04..1.04 rows=4 width=36) (actual time=0.020..0.021 rows=4 loops=3)                                                 |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                                    |
    |                                 ->  Seq Scan on mods_plan  (cost=0.00..1.04 rows=4 width=36) (actual time=0.015..0.015 rows=4 loops=3)                          |
    | Planning Time: 0.632 ms                                                                                                                                         |
    | Execution Time: 73.704 ms                                                                                                                                       |

    There is still no significant change in query efficiency. I assume this must be about as fast as this query can get because creating more indexes on the columns that this query depends on has stopped improving the query’s performance.


 - mods.py:

    SELECT COALESCE((SELECT SUM(items_ledger.credit_change) FROM items_ledger), 0) +
    COALESCE((SELECT SUM(mods_ledger.credit_change) FROM mods_ledger), 0) AS credits

    | QUERY PLAN                                                                                                                                            
    | Result  (cost=13172.70..13172.72 rows=1 width=8) (actual time=55.041..57.440 rows=1 loops=1)                                                          |
    |   InitPlan 1 (returns $1)                                                                                                                             |
    |     ->  Finalize Aggregate  (cost=6755.12..6755.13 rows=1 width=8) (actual time=37.433..37.489 rows=1 loops=1)                                        |
    |           ->  Gather  (cost=6754.90..6755.11 rows=2 width=8) (actual time=37.110..37.473 rows=3 loops=1)                                              |
    |                 Workers Planned: 2                                                                                                                    |
    |                 Workers Launched: 2                                                                                                                   |
    |                 ->  Partial Aggregate  (cost=5754.90..5754.91 rows=1 width=8) (actual time=31.111..31.113 rows=1 loops=3)                             |
    |                       ->  Parallel Seq Scan on items_ledger  (cost=0.00..5338.12 rows=166712 width=4) (actual time=0.011..16.628 rows=133342 loops=3) |
    |   InitPlan 2 (returns $3)                                                                                                                             |
    |     ->  Finalize Aggregate  (cost=6417.56..6417.57 rows=1 width=8) (actual time=17.600..19.942 rows=1 loops=1)                                        |
    |           ->  Gather  (cost=6417.35..6417.56 rows=2 width=8) (actual time=17.433..19.935 rows=3 loops=1)                                              |
    |                 Workers Planned: 2                                                                                                                    |
    |                 Workers Launched: 2                                                                                                                   |
    |                 ->  Partial Aggregate  (cost=5417.35..5417.36 rows=1 width=8) (actual time=14.450..14.451 rows=1 loops=3)                             |
    |                       ->  Parallel Seq Scan on mods_ledger  (cost=0.00..5000.68 rows=166668 width=4) (actual time=0.006..7.327 rows=133335 loops=3)   |
    | Planning Time: 0.667 ms                                                                                                                               |
    | Execution Time: 57.681 ms                                                                                                                             |

    This is a collection of available credit for the shop, based on items and mods. Both scans for valid items and aggregations cost a lot. For aggregates, it costs a lot in startup and execution.

        Create index credit_index on items_ledger (credit_change)

    | QUERY PLAN                                                                                                                                                                    
    | Result  (cost=12885.80..12885.81 rows=1 width=8) (actual time=46.771..50.196 rows=1 loops=1)                                                                                   |
    |   InitPlan 1 (returns $1)                                                                                                                                                      |
    |     ->  Finalize Aggregate  (cost=6468.22..6468.23 rows=1 width=8) (actual time=19.072..19.169 rows=1 loops=1)                                                                 |
    |           ->  Gather  (cost=6468.00..6468.21 rows=2 width=8) (actual time=18.926..19.160 rows=3 loops=1)                                                                       |
    |                 Workers Planned: 2                                                                                                                                             |
    |                 Workers Launched: 2                                                                                                                                            |
    |                 ->  Partial Aggregate  (cost=5468.00..5468.01 rows=1 width=8) (actual time=16.463..16.464 rows=1 loops=3)                                                      |
    |                       ->  Parallel Index Only Scan using credit_index on items_ledger  (cost=0.42..5051.31 rows=166677 width=4) (actual time=0.139..9.573 rows=133342 loops=3) |
    |                             Heap Fetches: 232                                                                                                                                  |
    |   InitPlan 2 (returns $3)                                                                                                                                                      |
    |     ->  Finalize Aggregate  (cost=6417.56..6417.57 rows=1 width=8) (actual time=27.691..31.017 rows=1 loops=1)                                                                 |
    |           ->  Gather  (cost=6417.35..6417.56 rows=2 width=8) (actual time=27.462..31.007 rows=3 loops=1)                                                                       |
    |                 Workers Planned: 2                                                                                                                                             |
    |                 Workers Launched: 2                                                                                                                                            |
    |                 ->  Partial Aggregate  (cost=5417.35..5417.36 rows=1 width=8) (actual time=23.663..23.664 rows=1 loops=3)                                                      |
    |                       ->  Parallel Seq Scan on mods_ledger  (cost=0.00..5000.68 rows=166668 width=4) (actual time=0.011..12.472 rows=133335 loops=3)                           |
    | Planning Time: 10.044 ms                                                                                                                                                       |
    | Execution Time: 50.339 ms                                                                                                                                                      |

    We only need the credits for this to work. I expected at least some minor performance boost from this index, and it worked quite well.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT mod_sku, SUM(qty_change)
    FROM mods_ledger
    GROUP BY mod_sku

    | QUERY PLAN                                                                                                                                        
    | Finalize GroupAggregate  (cost=6834.13..6835.14 rows=4 width=13) (actual time=56.980..60.875 rows=5 loops=1)                                       |
    |   Group Key: mod_sku                                                                                                                               |
    |   ->  Gather Merge  (cost=6834.13..6835.06 rows=8 width=13) (actual time=56.971..60.865 rows=13 loops=1)                                           |
    |         Workers Planned: 2                                                                                                                         |
    |         Workers Launched: 2                                                                                                                        |
    |         ->  Sort  (cost=5834.10..5834.11 rows=4 width=13) (actual time=49.475..49.477 rows=4 loops=3)                                              |
    |               Sort Key: mod_sku                                                                                                                    |
    |               Sort Method: quicksort  Memory: 25kB                                                                                                 |
    |               Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                      |
    |               Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                      |
    |               ->  Partial HashAggregate  (cost=5834.02..5834.06 rows=4 width=13) (actual time=49.430..49.431 rows=4 loops=3)                       |
    |                     Group Key: mod_sku                                                                                                             |
    |                     Batches: 1  Memory Usage: 24kB                                                                                                 |
    |                     Worker 0:  Batches: 1  Memory Usage: 24kB                                                                                      |
    |                     Worker 1:  Batches: 1  Memory Usage: 24kB                                                                                      |
    |                     ->  Parallel Seq Scan on mods_ledger  (cost=0.00..5000.68 rows=166668 width=9) (actual time=0.010..15.894 rows=133335 loops=3) |
    | Planning Time: 0.486 ms                                                                                                                            |
    | Execution Time: 61.230 ms                                                                                                                          |

    It seems like aggregation and merging results takes a lot of time. I would imagine anything within the “group by” section of the code needs to be indexed for great performance.

        Create index mod_index on mods_ledger (qty_change)

    | QUERY PLAN                                                                                                                                         
    | Finalize GroupAggregate  (cost=6834.13..6835.14 rows=4 width=13) (actual time=39.947..45.308 rows=5 loops=1)                                       |
    |   Group Key: mod_sku                                                                                                                               |
    |   ->  Gather Merge  (cost=6834.13..6835.06 rows=8 width=13) (actual time=39.938..45.297 rows=13 loops=1)                                           |
    |         Workers Planned: 2                                                                                                                         |
    |         Workers Launched: 2                                                                                                                        |
    |         ->  Sort  (cost=5834.10..5834.11 rows=4 width=13) (actual time=36.217..36.219 rows=4 loops=3)                                              |
    |               Sort Key: mod_sku                                                                                                                    |
    |               Sort Method: quicksort  Memory: 25kB                                                                                                 |
    |               Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                      |
    |               Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                      |
    |               ->  Partial HashAggregate  (cost=5834.02..5834.06 rows=4 width=13) (actual time=36.182..36.184 rows=4 loops=3)                       |
    |                     Group Key: mod_sku                                                                                                             |
    |                     Batches: 1  Memory Usage: 24kB                                                                                                 |
    |                     Worker 0:  Batches: 1  Memory Usage: 24kB                                                                                      |
    |                     Worker 1:  Batches: 1  Memory Usage: 24kB                                                                                      |
    |                     ->  Parallel Seq Scan on mods_ledger  (cost=0.00..5000.68 rows=166668 width=9) (actual time=0.008..11.682 rows=133335 loops=3) |
    | Planning Time: 0.597 ms                                                                                                                            |
    | Execution Time: 45.550 ms                                                                                                                          |

    Not as big of a performance boost as I had hoped, but shaving off 15ms probably scales better as we get to multiple millions or billions.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT item_id, item_sku, type, SUM(qty_change) AS qty_change FROM items_ledger
                                            JOIN items_plan ON items_ledger.item_id = items_plan.id
                                            WHERE items_plan.mod_id = 0 and items_ledger.customer_id = 0
                                            GROUP BY item_id, item_sku, type
                                            HAVING SUM(qty_change) > 0

    | QUERY PLAN                                                                                                                                     
    | Finalize GroupAggregate  (cost=7051.58..7199.60 rows=390 width=56) (actual time=60.552..63.626 rows=6 loops=1)                                           |
    |   Group Key: items_ledger.item_id, items_ledger.item_sku, items_plan.type                                                                                |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                                                             |
    |   ->  Gather Merge  (cost=7051.58..7175.22 rows=976 width=56) (actual time=59.211..63.606 rows=18 loops=1)                                               |
    |         Workers Planned: 2                                                                                                                               |
    |         Workers Launched: 2                                                                                                                              |
    |         ->  Partial GroupAggregate  (cost=6051.56..6062.54 rows=488 width=56) (actual time=50.841..53.549 rows=6 loops=3)                                |
    |               Group Key: items_ledger.item_id, items_ledger.item_sku, items_plan.type                                                                    |
    |               ->  Sort  (cost=6051.56..6052.78 rows=488 width=52) (actual time=50.402..51.284 rows=19534 loops=3)                                        |
    |                     Sort Key: items_ledger.item_id, items_ledger.item_sku, items_plan.type                                                               |
    |                     Sort Method: quicksort  Memory: 2181kB                                                                                               |
    |                     Worker 0:  Sort Method: quicksort  Memory: 1967kB                                                                                    |
    |                     Worker 1:  Sort Method: quicksort  Memory: 1896kB                                                                                    |
    |                     ->  Hash Join  (cost=17.54..6029.77 rows=488 width=52) (actual time=0.073..43.210 rows=19534 loops=3)                                |
    |                           Hash Cond: (items_ledger.item_id = items_plan.id)                                                                              |
    |                           ->  Parallel Seq Scan on items_ledger  (cost=0.00..5754.46 rows=97506 width=20) (actual time=0.012..29.969 rows=78457 loops=3) |
    |                                 Filter: (customer_id = 0)                                                                                                |
    |                                 Rows Removed by Filter: 54884                                                                                            |
    |                           ->  Hash  (cost=17.50..17.50 rows=3 width=36) (actual time=0.026..0.027 rows=6 loops=3)                                        |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                             |
    |                                 ->  Seq Scan on items_plan  (cost=0.00..17.50 rows=3 width=36) (actual time=0.018..0.021 rows=6 loops=3)                 |
    |                                       Filter: (mod_id = 0)                                                                                               |
    |                                       Rows Removed by Filter: 18                                                                                         |
    | Planning Time: 0.644 ms                                                                                                                                  |
    | Execution Time: 63.973 ms                                                                                                                                |

    Hash joins and aggregates cost significantly more here than other queries, likely because now there needs to be a join and an aggregation. Indexing the join variables seems like a good step.

        create index item_index on items_ledger (item_id, item_sku)

    | QUERY PLAN                                                                                                                                               
    | Finalize GroupAggregate  (cost=7051.58..7199.60 rows=390 width=56) (actual time=35.416..38.373 rows=6 loops=1)                                           |
    |   Group Key: items_ledger.item_id, items_ledger.item_sku, items_plan.type                                                                                |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                                                             |
    |   ->  Gather Merge  (cost=7051.58..7175.22 rows=976 width=56) (actual time=34.644..38.354 rows=18 loops=1)                                               |
    |         Workers Planned: 2                                                                                                                               |
    |         Workers Launched: 2                                                                                                                              |
    |         ->  Partial GroupAggregate  (cost=6051.56..6062.54 rows=488 width=56) (actual time=27.238..29.631 rows=6 loops=3)                                |
    |               Group Key: items_ledger.item_id, items_ledger.item_sku, items_plan.type                                                                    |
    |               ->  Sort  (cost=6051.56..6052.78 rows=488 width=52) (actual time=26.764..27.555 rows=19534 loops=3)                                        |
    |                     Sort Key: items_ledger.item_id, items_ledger.item_sku, items_plan.type                                                               |
    |                     Sort Method: quicksort  Memory: 2163kB                                                                                               |
    |                     Worker 0:  Sort Method: quicksort  Memory: 1937kB                                                                                    |
    |                     Worker 1:  Sort Method: quicksort  Memory: 1944kB                                                                                    |
    |                     ->  Hash Join  (cost=17.54..6029.77 rows=488 width=52) (actual time=0.066..22.575 rows=19534 loops=3)                                |
    |                           Hash Cond: (items_ledger.item_id = items_plan.id)                                                                              |
    |                           ->  Parallel Seq Scan on items_ledger  (cost=0.00..5754.46 rows=97506 width=20) (actual time=0.014..15.700 rows=78457 loops=3) |
    |                                 Filter: (customer_id = 0)                                                                                                |
    |                                 Rows Removed by Filter: 54884                                                                                            |
    |                           ->  Hash  (cost=17.50..17.50 rows=3 width=36) (actual time=0.024..0.025 rows=6 loops=3)                                        |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                             |
    |                                 ->  Seq Scan on items_plan  (cost=0.00..17.50 rows=3 width=36) (actual time=0.015..0.018 rows=6 loops=3)                 |
    |                                       Filter: (mod_id = 0)                                                                                               |
    |                                       Rows Removed by Filter: 18                                                                                         |
    | Planning Time: 0.727 ms                                                                                                                                  |
    | Execution Time: 38.677 ms                                                                                                                                |

    As an update, it turns out indexing the join and aggregated columns did not work, but indexing just the joined columns did. Doing join and aggregated produced results with an average about the same as the original explain, but with a higher deviation.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT * FROM items_plan WHERE NOT mod_id = 0

    | QUERY PLAN                                                                                               |
    | -------------------------------------------------------------------------------------------------------- |
    | Seq Scan on items_plan  (cost=0.00..17.50 rows=597 width=108) (actual time=0.014..0.019 rows=18 loops=1) |
    |   Filter: (mod_id <> 0)                                                                                  |
    |   Rows Removed by Filter: 6                                                                              |
    | Planning Time: 0.439 ms                                                                                  |
    | Execution Time: 0.178 ms                                                                                 |

    Pretty simple here. We’re doing a where clause, we might as well index that column. After all, if indexing is about giving a definitive address, this is probably a perfect application.

        create index item_plan_index on items_plan (mod_id)

    | QUERY PLAN                                                                                             |
    | ------------------------------------------------------------------------------------------------------ |
    | Seq Scan on items_plan  (cost=0.00..1.30 rows=23 width=108) (actual time=0.009..0.012 rows=18 loops=1) |
    |   Filter: (mod_id <> 0)                                                                                |
    |   Rows Removed by Filter: 6                                                                            |
    | Planning Time: 0.326 ms                                                                                |
    | Execution Time: 0.101 ms        

    An overall good performance boost as expected.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT mods_plan.id, mods_plan.sku, mods_plan.type, sum(qty_change) AS quantity
    FROM mods_ledger JOIN mods_plan ON mods_ledger.mod_id = mods_plan.id
    WHERE SKU <> 'BASIC'
    GROUP BY mods_plan.id, mods_plan.sku, mods_plan.type

    | QUERY PLAN                                                                                                                                               
    | Finalize GroupAggregate  (cost=7350.61..7564.94 rows=846 width=76) (actual time=48.848..52.085 rows=3 loops=1)                                           |
    |   Group Key: mods_plan.id                                                                                                                                |
    |   ->  Gather Merge  (cost=7350.61..7548.02 rows=1692 width=76) (actual time=48.840..52.076 rows=9 loops=1)                                               |
    |         Workers Planned: 2                                                                                                                               |
    |         Workers Launched: 2                                                                                                                              |
    |         ->  Sort  (cost=6350.58..6352.70 rows=846 width=76) (actual time=44.849..44.851 rows=3 loops=3)                                                  |
    |               Sort Key: mods_plan.id                                                                                                                     |
    |               Sort Method: quicksort  Memory: 25kB                                                                                                       |
    |               Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                            |
    |               Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                            |
    |               ->  Partial HashAggregate  (cost=6300.99..6309.45 rows=846 width=76) (actual time=44.826..44.830 rows=3 loops=3)                           |
    |                     Group Key: mods_plan.id                                                                                                              |
    |                     Batches: 1  Memory Usage: 49kB                                                                                                       |
    |                     Worker 0:  Batches: 1  Memory Usage: 49kB                                                                                            |
    |                     Worker 1:  Batches: 1  Memory Usage: 49kB                                                                                            |
    |                     ->  Hash Join  (cost=31.20..5471.57 rows=165884 width=72) (actual time=0.042..31.457 rows=99791 loops=3)                             |
    |                           Hash Cond: (mods_ledger.mod_id = mods_plan.id)                                                                                 |
    |                           ->  Parallel Seq Scan on mods_ledger  (cost=0.00..5000.68 rows=166668 width=8) (actual time=0.008..10.558 rows=133335 loops=3) |
    |                           ->  Hash  (cost=20.62..20.62 rows=846 width=68) (actual time=0.021..0.022 rows=3 loops=3)                                      |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                             |
    |                                 ->  Seq Scan on mods_plan  (cost=0.00..20.62 rows=846 width=68) (actual time=0.016..0.017 rows=3 loops=3)                |
    |                                       Filter: (sku <> 'BASIC'::text)                                                                                     |
    |                                       Rows Removed by Filter: 1                                                                                          |
    | Planning Time: 0.478 ms                                                                                                                                  |
    | Execution Time: 52.277 ms                                                                                                                                |

    Anything in the where or group by may be good for indexing, although I am now cautious to add all columns due to the previous results.

        create index mods_l_index on mods_plan (id, sku, type)

    | QUERY PLAN                                                                                                                                              
    | Finalize GroupAggregate  (cost=7527.90..7528.66 rows=3 width=76) (actual time=36.175..39.728 rows=3 loops=1)                                            |
    |   Group Key: mods_plan.id                                                                                                                               |
    |   ->  Gather Merge  (cost=7527.90..7528.60 rows=6 width=76) (actual time=36.168..39.720 rows=9 loops=1)                                                 |
    |         Workers Planned: 2                                                                                                                              |
    |         Workers Launched: 2                                                                                                                             |
    |         ->  Sort  (cost=6527.88..6527.89 rows=3 width=76) (actual time=33.669..33.671 rows=3 loops=3)                                                   |
    |               Sort Key: mods_plan.id                                                                                                                    |
    |               Sort Method: quicksort  Memory: 25kB                                                                                                      |
    |               Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                           |
    |               Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                           |
    |               ->  Partial HashAggregate  (cost=6527.82..6527.85 rows=3 width=76) (actual time=33.647..33.649 rows=3 loops=3)                            |
    |                     Group Key: mods_plan.id                                                                                                             |
    |                     Batches: 1  Memory Usage: 24kB                                                                                                      |
    |                     Worker 0:  Batches: 1  Memory Usage: 24kB                                                                                           |
    |                     Worker 1:  Batches: 1  Memory Usage: 24kB                                                                                           |
    |                     ->  Hash Join  (cost=1.09..5902.82 rows=125001 width=72) (actual time=0.030..23.387 rows=99791 loops=3)                             |
    |                           Hash Cond: (mods_ledger.mod_id = mods_plan.id)                                                                                |
    |                           ->  Parallel Seq Scan on mods_ledger  (cost=0.00..5000.68 rows=166668 width=8) (actual time=0.006..8.071 rows=133335 loops=3) |
    |                           ->  Hash  (cost=1.05..1.05 rows=3 width=68) (actual time=0.015..0.016 rows=3 loops=3)                                         |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB                                                                            |
    |                                 ->  Seq Scan on mods_plan  (cost=0.00..1.05 rows=3 width=68) (actual time=0.012..0.013 rows=3 loops=3)                  |
    |                                       Filter: (sku <> 'BASIC'::text)                                                                                    |
    |                                       Rows Removed by Filter: 1                                                                                         |
    | Planning Time: 0.411 ms                                                                                                                                 |
    | Execution Time: 39.870 ms                                                                                                                               |

    I decided here to try and add every column in a where, group, or join anyways, and it worked very well. Not as expected.

 - recommendations.py:

    SELECT id
        FROM customers
        WHERE name = 'Tiffany Alexander' AND role = 'SHIFTER'

    | QUERY PLAN                                                                                                                   |
    | ---------------------------------------------------------------------------------------------------------------------------- |
    | Index Scan using customers_name_key on customers  (cost=0.42..8.44 rows=1 width=4) (actual time=0.244..0.245 rows=1 loops=1) |
    |   Index Cond: (name = 'Tiffany Alexander'::text)                                                                             |
    |   Filter: (role = 'SHIFTER'::text)                                                                                           |
    | Planning Time: 0.322 ms                                                                                                      |
    | Execution Time: 0.320 ms                                                                                                     |

    This query is simple, and an index for the where clause columns will greatly affect speed. There exists a customer name key, but creating a key for both types will hopefully speed things up.

        create index cust_index on customers (name, role)

    | QUERY PLAN                                                                                                           |
    | -------------------------------------------------------------------------------------------------------------------- |
    | Index Scan using cust_index on customers  (cost=0.42..8.44 rows=1 width=4) (actual time=0.019..0.021 rows=1 loops=1) |
    |   Index Cond: ((name = 'Tiffany Alexander'::text) AND (role = 'SHIFTER'::text))                                      |
    | Planning Time: 0.349 ms                                                                                              |
    | Execution Time: 0.091 ms         

    Index shortened the execution time, as expected.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT item_vec FROM items_plan
JOIN items_ledger ON items_plan.id = items_ledger.item_id
 WHERE items_plan.type = 'fire'
GROUP BY item_vec
HAVING SUM(qty_change) > 0

    | QUERY PLAN                                                                                                      |
    | --------------------------------------------------------------------------------------------------------------- |
    | HashAggregate  (cost=4320.27..4320.28 rows=1 width=32) (actual time=0.155..0.156 rows=0 loops=1)                |
    |   Group Key: items_plan.item_vec                                                                                |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                    |
    |   Batches: 1  Memory Usage: 24kB                                                                                |
    |   ->  Nested Loop  (cost=189.60..4236.93 rows=16668 width=36) (actual time=0.153..0.154 rows=0 loops=1)         |
    |         ->  Seq Scan on items_plan  (cost=0.00..1.30 rows=1 width=36) (actual time=0.153..0.153 rows=0 loops=1) |
    |               Filter: (type = 'fire'::text)                                                                     |
    |               Rows Removed by Filter: 24                                                                        |
    |         ->  Bitmap Heap Scan on items_ledger  (cost=189.60..4068.95 rows=16668 width=8) (never executed)        |
    |               Recheck Cond: (item_id = items_plan.id)                                                           |
    |               ->  Bitmap Index Scan on item_index  (cost=0.00..185.43 rows=16668 width=0) (never executed)      |
    |                     Index Cond: (item_id = items_plan.id)                                                       |
    | Planning Time: 0.492 ms                                                                                         |
    | Execution Time: 0.257 ms                                                                                        |

    Expecting item_vec, type, and id to be relevant to the necessary index. The join and grouping are still expensive, however, and a marginal, but not significant, improvement is expected. I only say this because previous queries seem to follow that pattern. It’s interesting to see a hash aggregate and a loop that take an incredibly long time from the join and having terms.

        create index vec_index on items_plan (id, type, item_vec)

    | QUERY PLAN                                                                                                      |
    | --------------------------------------------------------------------------------------------------------------- |
    | HashAggregate  (cost=4320.27..4320.28 rows=1 width=32) (actual time=0.010..0.011 rows=0 loops=1)                |
    |   Group Key: items_plan.item_vec                                                                                |
    |   Filter: (sum(items_ledger.qty_change) > 0)                                                                    |
    |   Batches: 1  Memory Usage: 24kB                                                                                |
    |   ->  Nested Loop  (cost=189.60..4236.93 rows=16668 width=36) (actual time=0.009..0.009 rows=0 loops=1)         |
    |         ->  Seq Scan on items_plan  (cost=0.00..1.30 rows=1 width=36) (actual time=0.008..0.009 rows=0 loops=1) |
    |               Filter: (type = 'fire'::text)                                                                     |
    |               Rows Removed by Filter: 24                                                                        |
    |         ->  Bitmap Heap Scan on items_ledger  (cost=189.60..4068.95 rows=16668 width=8) (never executed)        |
    |               Recheck Cond: (item_id = items_plan.id)                                                           |
    |               ->  Bitmap Index Scan on item_index  (cost=0.00..185.43 rows=16668 width=0) (never executed)      |
    |                     Index Cond: (item_id = items_plan.id)                                                       |
    | Planning Time: 0.616 ms                                                                                         |
    | Execution Time: 0.153 ms                                                                                        |

    Better improvements than expected.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT sku, price FROM items_plan
WHERE item_vec = array[50,1,1]

    | QUERY PLAN                                                                                          |
    | --------------------------------------------------------------------------------------------------- |
    | Seq Scan on items_plan  (cost=0.00..1.30 rows=1 width=36) (actual time=0.022..0.027 rows=1 loops=1) |
    |   Filter: (item_vec = '{50,1,1}'::integer[])                                                        |
    |   Rows Removed by Filter: 23                                                                        |
    | Planning Time: 0.709 ms                                                                             |
    | Execution Time: 0.136 ms                                                                            |

    Another simpler query. Only one column is in the where clause that would be optimal to use. This is an incredibly low-cost query as the table is small and organized by default.

        create index vec_index on items_plan (item_vec)

    | QUERY PLAN                                                                                          |
    | --------------------------------------------------------------------------------------------------- |
    | Seq Scan on items_plan  (cost=0.00..1.30 rows=1 width=36) (actual time=0.029..0.034 rows=1 loops=1) |
    |   Filter: (item_vec = '{50,1,1}'::integer[])                                                        |
    |   Rows Removed by Filter: 23                                                                        |
    | Planning Time: 0.434 ms                                                                             |
    | Execution Time: 0.090 ms                                                                            |

    Several iterations of the query show that improvements are minor but semi-consistent.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT item_sku, customer_id, items_plan.type AS type
    FROM items_ledger
    JOIN items_plan ON items_plan.sku = items_ledger.item_sku
    WHERE customer_id = (SELECT id FROM customers
    WHERE name = 'Tiffany Alexander')
    GROUP BY item_sku, customer_id, items_plan.type
    HAVING SUM(qty_change) < 0
    ORDER BY items_plan.type ASC

    | QUERY PLAN                                                                                                                                        ------------------------------------------------------------------------------------------------------------------------------------------------- |
    | Finalize GroupAggregate  (cost=6764.73..6767.45 rows=7 width=48) (actual time=22.103..24.863 rows=1 loops=1)                                      |
    |   Group Key: items_plan.type, items_ledger.item_sku, items_ledger.customer_id                                                                     |
    |   Filter: (sum(items_ledger.qty_change) < 0)                                                                                                      |
    |   InitPlan 1 (returns $0)                                                                                                                         |
    |     ->  Index Scan using customers_name_key on customers  (cost=0.42..8.44 rows=1 width=4) (actual time=0.065..0.066 rows=1 loops=1)              |
    |           Index Cond: (name = 'Tiffany Alexander'::text)                                                                                          |
    |   ->  Gather Merge  (cost=6756.29..6758.57 rows=18 width=56) (actual time=22.096..24.854 rows=1 loops=1)                                          |
    |         Workers Planned: 2                                                                                                                        |
    |         Params Evaluated: $0                                                                                                                      |
    |         Workers Launched: 2                                                                                                                       |
    |         ->  Partial GroupAggregate  (cost=5756.27..5756.47 rows=9 width=56) (actual time=17.008..17.010 rows=0 loops=3)                           |
    |               Group Key: items_plan.type, items_ledger.item_sku, items_ledger.customer_id                                                         |
    |               ->  Sort  (cost=5756.27..5756.29 rows=9 width=52) (actual time=17.004..17.006 rows=0 loops=3)                                       |
    |                     Sort Key: items_plan.type, items_ledger.item_sku                                                                              |
    |                     Sort Method: quicksort  Memory: 25kB                                                                                          |
    |                     Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                               |
    |                     Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                               |
    |                     ->  Hash Join  (cost=1.54..5756.13 rows=9 width=52) (actual time=14.059..16.977 rows=0 loops=3)                               |
    |                           Hash Cond: (items_ledger.item_sku = items_plan.sku)                                                                     |
    |                           ->  Parallel Seq Scan on items_ledger  (cost=0.00..5754.46 rows=9 width=20) (actual time=14.028..16.945 rows=0 loops=3) |
    |                                 Filter: (customer_id = $0)                                                                                        |
    |                                 Rows Removed by Filter: 133341                                                                                    |
    |                           ->  Hash  (cost=1.24..1.24 rows=24 width=64) (actual time=0.041..0.041 rows=24 loops=1)                                 |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 10kB                                                                     |
    |                                 ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=64) (actual time=0.027..0.030 rows=24 loops=1)         |
    | Planning Time: 0.970 ms                                                                                                                           |
    | Execution Time: 25.083 ms                                                                                                                         |

    Subquery inside a large query makes this an incredibly expensive lookup. Particularly the group by aggregate function, the join, and the having clause.

        create index cust_collect_idx on items_ledger (item_sku, customer_id)

    | QUERY PLAN                                                                                                                                        ------------------------------------------------------------------------------------------------------------------------------------------------- |
    | GroupAggregate  (cost=213.00..213.52 rows=7 width=48) (actual time=0.316..0.317 rows=1 loops=1)                                                   |
    |   Group Key: items_plan.type, items_ledger.item_sku, items_ledger.customer_id                                                                     |
    |   Filter: (sum(items_ledger.qty_change) < 0)                                                                                                      |
    |   InitPlan 1 (returns $0)                                                                                                                         |
    |     ->  Index Scan using customers_name_key on customers  (cost=0.42..8.44 rows=1 width=4) (actual time=0.061..0.062 rows=1 loops=1)              |
    |           Index Cond: (name = 'Tiffany Alexander'::text)                                                                                          |
    |   ->  Sort  (cost=204.56..204.61 rows=21 width=52) (actual time=0.309..0.310 rows=1 loops=1)                                                      |
    |         Sort Key: items_plan.type, items_ledger.item_sku                                                                                          |
    |         Sort Method: quicksort  Memory: 25kB                                                                                                      |
    |         ->  Nested Loop  (cost=0.42..204.10 rows=21 width=52) (actual time=0.265..0.281 rows=1 loops=1)                                           |
    |               ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=64) (actual time=0.006..0.009 rows=24 loops=1)                           |
    |               ->  Index Scan using cust_collect_idx on items_ledger  (cost=0.42..8.44 rows=1 width=20) (actual time=0.008..0.008 rows=0 loops=24) |
    |                     Index Cond: ((item_sku = items_plan.sku) AND (customer_id = $0))                                                              |
    | Planning Time: 0.911 ms                                                                                                                           |
    | Execution Time: 0.468 ms                                                            

    Massive improvements overall, far more than what I expected. Considering the subquery, I wonder if the execution time will blow up nonlinearly as more rows are added.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT item_sku, customer_id, items_plan.type AS type
                                                FROM items_ledger
                                                JOIN items_plan ON items_plan.sku = items_ledger.item_sku
                                                WHERE customer_id = (SELECT id FROM customers
                                                WHERE name = 'Jason Mendoza')
                                                GROUP BY item_sku, customer_id, items_plan.type
                                                HAVING SUM(qty_change) < 0
                                                ORDER BY items_plan.type ASC

    | QUERY PLAN                                                                                                                                       |
    | ------------------------------------------------------------------------------------------------------------------------------------------------ |
    | Finalize GroupAggregate  (cost=6764.64..6767.66 rows=8 width=22) (actual time=11.255..15.162 rows=2 loops=1)                                     |
    |   Group Key: items_plan.type, items_ledger.item_sku, items_ledger.customer_id                                                                    |
    |   Filter: (sum(items_ledger.qty_change) < 0)                                                                                                     |
    |   InitPlan 1 (returns $0)                                                                                                                        |
    |     ->  Index Scan using customers_name_key on customers  (cost=0.42..8.44 rows=1 width=4) (actual time=0.022..0.022 rows=1 loops=1)             |
    |           Index Cond: (name = 'Jason Mendoza'::text)                                                                                             |
    |   ->  Gather Merge  (cost=6756.21..6758.74 rows=20 width=30) (actual time=11.252..15.159 rows=2 loops=1)                                         |
    |         Workers Planned: 2                                                                                                                       |
    |         Params Evaluated: $0                                                                                                                     |
    |         Workers Launched: 2                                                                                                                      |
    |         ->  Partial GroupAggregate  (cost=5756.18..5756.41 rows=10 width=30) (actual time=9.240..9.241 rows=1 loops=3)                           |
    |               Group Key: items_plan.type, items_ledger.item_sku, items_ledger.customer_id                                                        |
    |               ->  Sort  (cost=5756.18..5756.21 rows=10 width=26) (actual time=9.236..9.237 rows=1 loops=3)                                       |
    |                     Sort Key: items_plan.type, items_ledger.item_sku                                                                             |
    |                     Sort Method: quicksort  Memory: 25kB                                                                                         |
    |                     Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                              |
    |                     Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                              |
    |                     ->  Hash Join  (cost=1.54..5756.02 rows=10 width=26) (actual time=7.085..9.219 rows=1 loops=3)                               |
    |                           Hash Cond: (items_ledger.item_sku = items_plan.sku)                                                                    |
    |                           ->  Parallel Seq Scan on items_ledger  (cost=0.00..5754.34 rows=10 width=20) (actual time=7.075..9.208 rows=1 loops=3) |
    |                                 Filter: (customer_id = $0)                                                                                       |
    |                                 Rows Removed by Filter: 133333                                                                                   |
    |                           ->  Hash  (cost=1.24..1.24 rows=24 width=18) (actual time=0.015..0.015 rows=24 loops=1)                                |
    |                                 Buckets: 1024  Batches: 1  Memory Usage: 10kB                                                                    |
    |                                 ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=18) (actual time=0.007..0.009 rows=24 loops=1)        |
    | Planning Time: 0.305 ms                                                                                                                          |
    | Execution Time: 15.225 ms                                                                                                                        |

    This query plan indicates that items_ledger is slowing down the query. So, and index on it may be helpful.

        CREATE INDEX items_ledger_item_sku_customer_id ON items_ledger (item_sku, customer_id);

    | QUERY PLAN                                                                                                                                                         |
    | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | GroupAggregate  (cost=213.06..213.63 rows=8 width=22) (actual time=0.212..0.213 rows=2 loops=1)                                                                    |
    |   Group Key: items_plan.type, items_ledger.item_sku, items_ledger.customer_id                                                                                      |
    |   Filter: (sum(items_ledger.qty_change) < 0)                                                                                                                       |
    |   InitPlan 1 (returns $0)                                                                                                                                          |
    |     ->  Index Scan using customers_name_key on customers  (cost=0.42..8.44 rows=1 width=4) (actual time=0.042..0.042 rows=1 loops=1)                               |
    |           Index Cond: (name = 'Jason Mendoza'::text)                                                                                                               |
    |   ->  Sort  (cost=204.62..204.68 rows=23 width=26) (actual time=0.208..0.209 rows=2 loops=1)                                                                       |
    |         Sort Key: items_plan.type, items_ledger.item_sku                                                                                                           |
    |         Sort Method: quicksort  Memory: 25kB                                                                                                                       |
    |         ->  Nested Loop  (cost=0.42..204.10 rows=23 width=26) (actual time=0.098..0.197 rows=2 loops=1)                                                            |
    |               ->  Seq Scan on items_plan  (cost=0.00..1.24 rows=24 width=18) (actual time=0.003..0.004 rows=24 loops=1)                                            |
    |               ->  Index Scan using items_ledger_item_sku_customer_id on items_ledger  (cost=0.42..8.44 rows=1 width=20) (actual time=0.006..0.006 rows=0 loops=24) |
    |                     Index Cond: ((item_sku = items_plan.sku) AND (customer_id = $0))                                                                               |
    | Planning Time: 0.429 ms                                                                                                                                            |
    | Execution Time: 0.283 ms                                                                                                                                           |

    The index made the query more efficient as expected.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT recent_w_rec, recent_a_rec, recent_o_rec FROM customers 
                                               WHERE name = 'Jason Mendoza'

    | QUERY PLAN                                                                                                                    |
    | ----------------------------------------------------------------------------------------------------------------------------- |
    | Index Scan using customers_name_key on customers  (cost=0.42..8.44 rows=1 width=35) (actual time=0.178..0.178 rows=1 loops=1) |
    |   Index Cond: (name = 'Jason Mendoza'::text)                                                                                  |
    | Planning Time: 0.439 ms                                                                                                       |
    | Execution Time: 0.233 ms                                                                                                      |

    This query is already fast. However, it may be worth creating an index on the name of the customer because the query depends on it.

        CREATE INDEX customers_name_idx ON customers (name)

    | QUERY PLAN                                                                                                                    |
    | ----------------------------------------------------------------------------------------------------------------------------- |
    | Index Scan using customers_name_idx on customers  (cost=0.42..8.44 rows=1 width=35) (actual time=0.018..0.018 rows=1 loops=1) |
    |   Index Cond: (name = 'Jason Mendoza'::text)                                                                                  |
    | Planning Time: 0.277 ms                                                                                                       |
    | Execution Time: 0.059 ms                                                                                                      |

    The query became faster as I expected.

    ----------------------------------------------------------------------------------------------------------------------------------------

    SELECT id, price FROM items_plan
                                                         WHERE sku = :x

    | QUERY PLAN                                                                                         |
    | -------------------------------------------------------------------------------------------------- |
    | Seq Scan on items_plan  (cost=0.00..1.30 rows=1 width=8) (actual time=0.015..0.016 rows=1 loops=1) |
    |   Filter: (sku = 'CHAINLINK'::text)                                                                |
    |   Rows Removed by Filter: 23                                                                       |
    | Planning Time: 0.254 ms                                                                            |
    | Execution Time: 0.092 ms                                                                           |

    This query is fast. However, it is worth trying to make it faster because items_plan is not updated throughout our code. An index on items_plan may be helpful.

        CREATE INDEX items_plan_sku_idx ON items_plan (sku);

    | QUERY PLAN                                                                                         |
    | -------------------------------------------------------------------------------------------------- |
    | Seq Scan on items_plan  (cost=0.00..1.30 rows=1 width=8) (actual time=0.009..0.010 rows=1 loops=1) |
    |   Filter: (sku = 'CHAINLINK'::text)                                                                |
    |   Rows Removed by Filter: 23                                                                       |
    | Planning Time: 0.186 ms                                                                            |
    | Execution Time: 0.052 ms                                                                           |

    The index made the query faster as I expected.
