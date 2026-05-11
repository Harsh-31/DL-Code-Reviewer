-- sample.sql — user orders query with intentional issues for review testing

-- BUG 1: SELECT * leaks schema and breaks on column changes
-- BUG 2: No LIMIT — could return millions of rows
-- BUG 3: Hardcoded date string instead of parameter
-- BUG 4: No index hint on high-cardinality join

SELECT *
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
  AND o.created_at > '2024-01-01'
ORDER BY o.created_at DESC;
