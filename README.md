Entity Similarity
------------------
Code base to compute similarity score between entities.

Methodology:
------
Precondition: Data should contain a entity, category column, a string metric and a numeric metric column at the category level.
PostCondition : A similarity score between 0 and 1, where 1 indicated highly similar(may not be exact same values).

Assumption: Similarity is computed at entity and category level, assuming that comparison across categories may not be valid.

Steps:
1. Similarity among string metrics are computed and are clustered together (group).
2. Data is aggreagted at entity, category and group level
3. Similarity for a given entity with others is computed as follows
  a. For each category similarity is computed for numeric metric
  b. A weighted average is calculated based on ratio of metric
  c. Other entities are sorted and top 3 macthes are picked
 
 Kindly reachout to binukeloth@gmail.com for queries.
