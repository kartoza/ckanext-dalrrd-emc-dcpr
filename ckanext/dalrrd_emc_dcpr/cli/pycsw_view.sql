CREATE MATERIALIZED VIEW public.emc_pycsw_view AS
    WITH cte_extras AS (
        SELECT
               p.id,
               p.title,
               p.name,
               p.metadata_created,
               p.notes,
               g.title AS org_name,
               json_object_agg(pe.key, pe.value) AS extras
        FROM package AS p
            JOIN package_extra AS pe ON p.id = pe.package_id
            JOIN "group" AS g ON p.owner_org = g.id
        GROUP BY p.id, g.title
    )
    SELECT
           c.id AS identifier,
           c.title AS title,
           c.name AS title_alternate,
           c.notes AS abstract,
           c.metadata_created AS insert_date,
           c.org_name AS organization,
           c.extras->'metadata_language' AS metadata_language,
           c.extras->'iso_topic_category' AS iso_topic_category,
           c.extras->'lineage' AS lineage,
           c.extras->'dataset_language' AS language,
           c.extras->'spatial_reference_system' AS crs
    FROM cte_extras AS c
WITH DATA

DROP MATERIALIZED VIEW emc_pycsw_view

CREATE UNIQUE INDEX idx_id ON emc_pycsw_view ( identifier)
