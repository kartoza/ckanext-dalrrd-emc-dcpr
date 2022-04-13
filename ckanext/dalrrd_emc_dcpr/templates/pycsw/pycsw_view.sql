CREATE MATERIALIZED VIEW IF NOT EXISTS {{ view_name }} AS
    WITH cte_extras AS (
        SELECT
               p.id,
               p.title,
               p.name,
               p.metadata_created,
               p.metadata_modified,
               p.notes,
               p.author,
               g.title AS org_name,
               p.maintainer,
               json_object_agg(pe.key, pe.value) AS extras,
               array_agg(DISTINCT t.name) AS tags
        FROM package AS p
            JOIN package_extra AS pe ON p.id = pe.package_id
            JOIN "group" AS g ON p.owner_org = g.id
            JOIN package_tag AS pt ON p.id = pt.package_id
            JOIN tag AS t on pt.tag_id = t.id
        WHERE p.state = 'active'
         AND p.private = false
        GROUP BY p.id, g.title
    )
    SELECT
           c.id AS identifier,
           'csw:Record' AS typename,
           'http://www.isotc211.org/2005/gmd' AS schema,
           'local' AS mdsource,
           c.metadata_created AS insert_date,
           NULL AS xml,
           NULL AS metadata,
           NULL AS metadata_type,
           concat_ws(' ', c.name, c.notes) AS anytext,
           c.extras->>'metadata_language' AS language,
           c.title AS title,
           c.notes AS abstract,
           concat_ws(', ', VARIADIC c.tags) AS keywords,
           NULL AS keywordstype,
           NULL AS format,
           NULL AS source,
           c.extras->>'reference_date' AS date,
           c.metadata_modified AS date_modified,
           'http://purl.org/dc/dcmitype/Dataset' AS type,
           ST_AsText(ST_GeomFromGeoJSON(c.extras->>'spatial')) AS wkt_geometry,
           ST_GeomFromGeoJSON(c.extras->>'spatial')::geometry(Polygon, 4326) AS wkb_geometry,
           c.extras->>'spatial_reference_system' AS crs,
           c.name AS title_alternate,
           NULL as date_revision,
           c.metadata_created AS date_creation,
           NULL AS date_publication,
           c.org_name AS organization,
           NULL AS securityconstraints,
           NULL AS parentidentifier,
           c.extras->>'iso_topic_category' AS topiccategory,
           c.extras->>'dataset_language' AS resourcelanguage,
           NULL AS geodescode,
           NULL AS denominator,
           NULL AS distancevalue,
           NULL AS distanceuom,
           c.extras->>'reference_date' AS time_begin,
           c.extras->>'reference_date' AS time_end,
           NULL AS servicetype,
           NULL AS servicetypeversion,
           NULL AS operation,
           NULL AS couplingtype,
           NULL AS operateson,
           NULL AS operatesonidentifier,
           NULL AS operatesonname,
           NULL AS degree,
           NULL AS accessconstraints,
           NULL AS otherconstraints,
           NULL AS classification,
           NULL AS conditionapplyingtoaccessanduse,
           c.extras->>'lineage' AS lineage,
           NULL AS responsiblepartyrole,
           NULL AS specificationtitle,
           NULL AS specificationdate,
           NULL AS specificationdatetype,
           c.author AS creator,
           c.maintainer AS publisher,
           NULL AS contributor,
           NULL AS relation,
           NULL AS platform,
           NULL AS instrument,
           NULL AS sensortype,
           NULL AS cloudcover,
           NULL AS bands,
           -- links: list of dicts with properties: name, description, protocol, url
           NULL AS links
    FROM cte_extras AS c
WITH DATA;
