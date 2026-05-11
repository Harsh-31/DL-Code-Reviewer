# SQL Review Guidelines

## Performance
- Avoid `SELECT *` — always specify columns explicitly
- Ensure JOIN columns are indexed
- Use `LIMIT` on queries that could return large result sets
- Avoid functions on indexed columns in WHERE clauses (prevents index use)
- Prefer `EXISTS` over `IN` for subqueries on large tables

## Correctness
- Watch for implicit type coercions in comparisons
- NULL handling: `IS NULL` / `IS NOT NULL`, not `= NULL`
- Be explicit about JOIN type (INNER, LEFT, RIGHT)
- Check for off-by-one in date range queries (exclusive vs inclusive bounds)

## Security
- Never interpolate user input directly — use parameterized queries
- Avoid dynamic SQL construction where possible
- Check for privilege escalation risks in stored procedures

## Readability
- Use CTEs (`WITH` clauses) instead of deeply nested subqueries
- Alias all tables for clarity
- Hardcoded string literals and dates should be parameters or constants
