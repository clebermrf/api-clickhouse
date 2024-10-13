-- From the two most commonly appearing regions, which is the latest datasource?
WITH two_most_frequent_regions AS (
    SELECT
        region
    FROM
        trips
    GROUP BY
        region
    ORDER BY 
        count() DESC
    LIMIT 2
)

SELECT
    argMax(datasource, datetime) AS latest_datasource -- This is faster than order by + limit 1
FROM
    trips
WHERE 
    region IN two_most_frequent_regions


-- What regions has the "cheap_mobile" datasource appeared in?
SELECT DISTINCT
    region
FROM
    trips
WHERE
    datasource = 'cheap_mobile'
