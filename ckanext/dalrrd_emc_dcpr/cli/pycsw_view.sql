CREATE MATERIALIZED VIEW public.emc_pycsw_view AS
    WITH cte_extras AS (
        SELECT
               p.id,
               p.title,
               p.name,
               p.metadata_created,
               p.notes,
               g.title AS org_name,
               json_object_agg(pe.key, pe.value) AS extras,
               array_agg(DISTINCT t.name) AS tags
        FROM package AS p
            JOIN package_extra AS pe ON p.id = pe.package_id
            JOIN "group" AS g ON p.owner_org = g.id
            JOIN package_tag AS pt ON p.id = pt.package_id
            JOIN tag AS t on pt.tag_id = t.id
        GROUP BY p.id, g.title
    )
    SELECT
           c.id AS identifier,
           'csw:Record' AS typename,
           'http://www.isotc211.org/2005/gmd' AS schema,
           'local' AS mdsource,
           c.metadata_created AS insert_date,
           c.title AS title,
           c.name AS title_alternate,
           c.notes AS abstract,
           'http://purl.org/dc/dcmitype/Dataset' AS type,
           null AS parentidentifier,
           c.org_name AS organization,
           c.extras->'metadata_language' AS metadata_language,
           c.extras->'iso_topic_category' AS iso_topic_category,
           c.extras->'lineage' AS lineage,
           c.extras->'dataset_language' AS language,
           c.extras->'spatial_reference_system' AS crs,
           concat_ws(', ', VARIADIC c.tags) AS keywords,
           concat_ws(' ', c.name, c.notes) AS anytext,
           ST_AsText(ST_GeomFromGeoJSON(c.extras->>'spatial')) AS wkt_geometry
    FROM cte_extras AS c
WITH DATA

DROP MATERIALIZED VIEW emc_pycsw_view

CREATE UNIQUE INDEX idx_id ON emc_pycsw_view ( identifier)
