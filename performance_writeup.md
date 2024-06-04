Fake Data Modeling

python file that creates fake rows: populate.py

We decided to distribute the million rows by having 200,000 rows in “customers,” 400,000 entries in the “items_ledger,” and 400,000 entries in the “mods_ledger.” We chose these values because we wanted to simulate item and modification purchases from our shopkeeper and transactions from our customers. Also, while 200,000 unique customers seems like a lot, we have a lot of items to sell so with this set of fake data it is logical to have a lot of people show up to our shop. Furthermore, we did not add any rows to “items_plan” or “mods_plan” because our code never adds to the list of possible items that we can sell and the modifications that we apply to those items.



Performance Results of Hitting Endpoints



Performance Tuning

 - Catalog.py:

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


 - mods.py

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

3
