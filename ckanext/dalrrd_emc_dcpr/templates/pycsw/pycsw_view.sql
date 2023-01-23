CREATE MATERIALIZED VIEW IF NOT EXISTS {{ view_name }} AS
    WITH

    -- cte_resources AS (
    --     select
    --     "resource".package_id,
    --     "resource".name,
    --     "resource".url,
    --     "resource".description as res
    --     from "resource"
    -- ),

    cte_extras AS (
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
               --json_object_agg('url', res.url) as links
               --array_agg(ARRAY[DISTINCT res.url ::text, res.name ::text, res.description ::text]) as links
               -- array_agg() as links_urls,
               -- array_agg(DISTINCT ) as links_descriptions
        FROM package AS p
            JOIN package_extra AS pe ON p.id = pe.package_id
            JOIN "group" AS g ON p.owner_org = g.id
            JOIN package_tag AS pt ON p.id = pt.package_id
            JOIN tag AS t on pt.tag_id = t.id
            JOIN "resource" as res on p.id = res.package_id
        WHERE p.state = 'active'
        AND p.private = false
        GROUP BY p.id, g.title
    )
    SELECT
           c.id AS identifier,
           c.name AS dataset_name,
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
           c.extras->>'reference_date-0-reference' AS date,
           c.extras->>'reference_date-0-date_type' AS reference_date_type,
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
           c.extras->>'purpose' AS purpose,
           c.extras->>'status' AS status,
           c.extras->>'metadata_standard_name' AS metadata_standard,
           c.extras->>'metadata_standard_version' AS metadata_standard_version,
           c.extras->>'dataset_character_set' AS dataset_character_set,
           c.extras->>'metadata_character_set' AS metadata_character_set,
           c.extras->>'metadata_date_stamp' AS metadata_date_stamp,
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
	       NULL AS edition,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'level' AS lineage_level,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'statement' AS lineage_statement,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'process_step_description' AS lineage_process_step_description,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'process_step_rationale' AS lineage_process_step_rationale,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'process_step_datetime_from' AS lineage_process_step_datetime_from,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'process_step_datetime_to' AS lineage_process_step_datetime_to,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processor_individual_name' AS lineage_processor_individual_name,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processing_owner_org' AS lineage_processing_organization,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processor_position_name' AS lineage_processor_position_name,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'delivery_point' AS lineage_delivery_point,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processor_address_city' AS lineage_processor_address_city,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processor_address_administrative_area' AS lineage_processor_address_administrative_area,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processor_postal_code' AS lineage_processor_postal_code,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'processor_electronic_mail_address' AS lineage_processor_electronic_mail_address,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'source_description' AS lineage_source_description,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'source_scale_denominator' AS lineage_source_scale_denominator,
           cast(cast(c.extras->>'dataset_lineage' as json)->>0 as json)-> 'source_reference_system' AS lineage_source_reference_system,
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
           -- contact
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'individual_name' AS contact_individual_name,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'position_name' AS contact_position_name,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'organisational_role' AS contact_organisational_role,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'delivery_point' AS contact_delivery_point,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'address_city' AS contact_address_city,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'address_administrative_area' AS contact_address_administrative_area,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'postal_code' AS contact_postal_code,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'electronic_mail_address' AS contact_electronic_mail_address,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'voice' AS contact_phone,
           cast(cast(c.extras->>'contact' as json)->>0 as json)-> 'facsimile' AS contact_facsimile,
           -- spatial and equivalent scale
           cast(c.extras->>'spatial' as json) AS bounding_geojson,
           c.extras->>'equivalent_scale' AS equivalent_scale,
           -- resources and distribution info
           -- distribution -> dict of distribution info and resource info.
            -- distribution info (resource name, version, compression, amdendment, sepc) + distributor info + process order info
            -- distributor info -> name, org name, position, role, contact [voice, facsimile, city,..etc.]
            -- order process info -> (fee, planned_available_date, instructions, ..etc)
            -- order transfer options -> (online, offline).
            -- resource info -> dicts with properties: name, description, protocol, url
           (select json_agg(json_build_object('url',res.url, 'name', res.name,'description',res.description ,'extras', res.extras))
            -- ARRAY[json_agg(to_json(res.extras), to_json(res.url))]
            --"res_url",res.url,"res_name",res.name, "res_description",res.description
            -- cast(res.extras as json)->>'application_profile',
            -- cast(res.extras as json)->>'amendment_number',
            -- cast(res.extras as json)->>'specification',
            -- cast(res.extras as json)->>'file_decompression_technique',
            -- cast(res.extras as json)->>'format_version',
            -- cast(cast(cast(cast(res.extras as json)->>'distributor' as json)->>0 as json)->'name' as text)
            -- cast(cast(cast(cast(res.extras as json)->>'distributor' as json)->>0 as json)->'organization_name' as text)
            -- cast(cast(cast(cast(res.extras as json)->>'distributor' as json)->>0 as json)->'position_name' as text)
            -- cast(cast(cast(cast(res.extras as json)->>'distributor' as json)->>0 as json)->'role' as text)
            -- cast(cast(cast(cast(res.extras as json)->>'distributor' as json)->>0 as json)->'role' as text)

            -- two things: return the distributor and work with renaming inisde array.

            from "resource" as res where res.package_id = c.id) AS links,
           -- temporal extent
           cast(cast(c.extras->>'reference_system_additional_info' as json)->>0 as json)-> 'temporal_extent_period_duration_from' AS temporal_position_begin,
           cast(cast(c.extras->>'reference_system_additional_info' as json)->>0 as json)-> 'temporal_extent_period_duration_to' AS temporal_position_end,
           -- vertical extents
           cast(cast(c.extras->>'reference_system_additional_info' as json)->>0 as json)-> 'minimum_vertical_extent' AS minimum_vertical_ex,
           cast(cast(c.extras->>'reference_system_additional_info' as json)->>0 as json)-> 'maximum_vertical_extent' AS maximum_vertical_ex



    FROM cte_extras AS c
    -- JOIN cte_resources as res on res.package_id = c.id
WITH DATA;
