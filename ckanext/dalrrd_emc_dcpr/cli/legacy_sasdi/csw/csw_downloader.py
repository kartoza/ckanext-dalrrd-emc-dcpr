import concurrent.futures
import dataclasses
import datetime as dt
import enum
import json
import logging
import typing
from functools import partial
from pathlib import Path

import httpx
from lxml import etree

from ckanext.dalrrd_emc_dcpr.constants import ISO_TOPIC_CATEGORIES
from ckanext.dalrrd_emc_dcpr.cli import _CkanEmcDataset, _CkanResource, utils
from ckanext.dalrrd_emc_dcpr.cli.legacy_sasdi import import_mappings

logger = logging.getLogger(__name__)

CSW_NAMESPACES: typing.Final[typing.Dict[str, str]] = {
    "csw": "http://www.opengis.net/cat/csw/2.0.2",
    "gmd": "http://www.isotc211.org/2005/gmd",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dct": "http://purl.org/dc/terms/",
    "ows": "http://www.opengis.net/ows",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


class CswGetRecordsResultType(enum.Enum):
    HITS = "hits"
    RESULTS = "results"
    VALIDATE = "validate"


class CswOutputFormat(enum.Enum):
    XML = "application/xml"


class CswOutputSchema(enum.Enum):
    CSW = "http://www.opengis.net/cat/csw/2.0.2"


class CswTypeName(enum.Enum):
    CSW_RECORD = "csw:Record"


class CswElementSetName(enum.Enum):
    BRIEF = "brief"
    FULL = "full"
    SUMMARY = "summary"


@dataclasses.dataclass
class CswRecord:
    identifier: str
    title: str
    abstract: str
    keywords: typing.List[str]
    type: str
    format: str
    author: str
    custodian: str
    repository: str
    source: str
    link: str
    thumbnail: str
    coverage: str
    bbox: str
    create_date: typing.Optional[dt.date]
    change_date: typing.Optional[dt.date]
    subjects: typing.List[str]

    def mapped_owner_org(self) -> typing.Optional[str]:
        result = None
        for name, aliases in import_mappings.CUSTODIAN_MAP.items():
            for alias in aliases:
                if alias.lower() in self.custodian.lower():
                    result = name
                    break
            if result is not None:
                break
        return result

    def to_data_dict(self, owner_user: str) -> typing.Dict:
        return self._to_ckan_dataset(
            owner_user, owner_org=self.mapped_owner_org() or "ingestion_org"
        ).to_data_dict()

    def _to_ckan_dataset(self, owner_user: str, owner_org: str) -> _CkanEmcDataset:
        min_lon, min_lat, max_lon, max_lat = self.bbox.split()
        bbox = {
            "type": "Polygon",
            "coordinates": [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ],
        }
        resources = []
        if self.link is not None:
            resources.append(
                _CkanResource(
                    url=self.link,
                    format="dummy",
                    format_version="0",
                )
            )
        return _CkanEmcDataset(
            name=self.title,
            private=True,
            notes=self.abstract,
            reference_date="2022-01-01",
            iso_topic_category=ISO_TOPIC_CATEGORIES[0][0],
            owner_org=owner_org,
            maintainer=owner_user,
            resources=resources,
            spatial=json.dumps(bbox),
            equivalent_scale="0",  # absurd value, to be corrected manually
            spatial_representation_type="001",  # dummy value, to be corrected manually
            spatial_reference_system="EPSG:4326",
            dataset_language="en",
            metadata_language="en",
            dataset_character_set="utf-8",
            maintainer_email=None,
            type="dataset",
            sasdi_theme=None,
            tags=[
                {"name": k, "vocabulary_id": None}
                for k in self.keywords + self.subjects
            ],
            source=self.source,
        )


def find_total_records(
    url, *, client: httpx.Client, xml_parser: etree.XMLParser
) -> typing.Optional[int]:
    get_records_response = _perform_get_records(
        url,
        {
            "result_type": CswGetRecordsResultType.HITS.value,
            "start_position": 1,
            "max_records": 0,
            "output_format": CswOutputFormat.XML.value,
            "output_schema": CswOutputSchema.CSW.value,
            "typename": CswTypeName.CSW_RECORD.value,
            "element_set_name": CswElementSetName.SUMMARY.value,
        },
        client=client,
        xml_parser=xml_parser,
    )
    existing_records = _get_num_records(get_records_response, namespaces=CSW_NAMESPACES)
    return existing_records[0] if existing_records is not None else None


def download_records(
    url: str,
    *,
    limit: int,
    offset: int,
    client: httpx.Client,
    xml_parser: etree.XMLParser,
) -> typing.List[etree.Element]:
    logger.debug(f"{locals()=}")
    get_records_response = _perform_get_records(
        url,
        {
            "result_type": CswGetRecordsResultType.RESULTS.value,
            "start_position": offset + 1,
            "max_records": limit,
            "output_format": CswOutputFormat.XML.value,
            "output_schema": CswOutputSchema.CSW.value,
            "typename": CswTypeName.CSW_RECORD.value,
            "element_set_name": CswElementSetName.FULL.value,
        },
        client=client,
        xml_parser=xml_parser,
    )
    existing_records = _get_num_records(get_records_response, namespaces=CSW_NAMESPACES)
    records = []
    if existing_records is not None:
        for record_el in get_records_response.xpath(
            "csw:SearchResults/*", namespaces=CSW_NAMESPACES
        ):
            records.append(record_el)
    return records


def save_records(
    records: typing.List[etree.Element],
    namespaces: typing.Dict[str, str],
    output_dir: Path,
) -> typing.List[Path]:
    output_dir.mkdir(exist_ok=True, parents=True)
    result = []
    for index, record in enumerate(records):
        identifier = _extract_record_identifier(record, namespaces=namespaces)
        if identifier is not None:
            output_path = output_dir / f"{identifier}.xml"
            output_path.write_bytes(etree.tostring(record, pretty_print=True))
            result.append(output_path)
        else:
            logger.warning(
                f"Unable to extract identifier from record {index!r}, skipping..."
            )
    return result


def parse_record(
    target_path: Path,
    namespaces: typing.Dict[str, str],
    *,
    xml_parser: etree.XMLParser,
) -> CswRecord:
    root_el = etree.fromstring(target_path.read_bytes(), parser=xml_parser)
    _retriever = partial(_retrieve_text, root_el, namespaces=namespaces)
    return CswRecord(
        identifier=_retriever("dc:identifier"),
        title=_retriever("dc:title"),
        abstract=_retriever("dc:abstract"),
        keywords=_parse_keywords(_retriever("dc:keywords")),
        type=_retriever("dc:type"),
        format=_retriever("dc:format"),
        author=_retriever("dc:author"),
        custodian=_retriever("dc:custodian"),
        repository=_retriever("dc:repository"),
        source=_retriever("dc:source"),
        link=_retriever("dc:link"),
        thumbnail=_retriever("dc:thumbnail"),
        coverage=_retriever("dc:coverage"),
        bbox=_retriever("dc:bbox"),
        create_date=_retriever("dc:createdate"),
        change_date=_retriever("dc:changedate"),
        subjects=_retriever("dc:subject", is_multiple=True),
    )


def import_record(record: CswRecord, user_name: str):
    """Import a parsed record into the CKAN database"""
    owner_user = None
    owner_org = None
    # data_dict = record.to_ckan_dataset(owner_user, owner_org).to_data_dict()
    # utils.create_single_dataset()


def retrieve_record_thumbnails(
    records: typing.List[CswRecord], output_dir: Path, *, client: httpx.Client
):
    for record in records:
        retrieve_thumbnail(record, output_dir, client=client)


def retrieve_thumbnail(
    record: CswRecord,
    output_dir: Path,
    *,
    client: httpx.Client,
) -> typing.Optional[Path]:
    """Retrieve record thumbnail

    Retrieve or try to create a thumbnail for the input record.

    Start by trying to fetch an already created thumbnail from the `record.thumbnail`
    attribute. If that does not work, then try to fetch the record link using
    rasterio and save an image from it

    """
    result = None
    output_dir.mkdir(exist_ok=True, parents=True)
    if record.thumbnail is not None:
        try:
            response = client.get(record.thumbnail)
        except httpx.ConnectError:
            logger.exception(
                f"Could not retrieve record.thumbnail ({record.thumbnail})"
            )
        else:
            if response.status_code == httpx.codes.OK:
                content_type = response.headers["Content-Type"]
                out_extension = content_type.rpartition("/")[-1]
                output_path = output_dir / f"{record.identifier}.{out_extension}"
                output_path.write_bytes(response.content)
                result = output_path
    # if not success:
    #     if record.source is not None and record.source.startswith("http"):
    #         # it can be a format recognizable by rasterio, in which case we try to
    #         # load it, downsample and save into a jpg to serve as a thumbnail
    #         # what if it is not loadable with rasterio?
    #         source_response = client.get(record.source)
    #         if source_response.status_code == httpx.codes.OK:
    #             response_mime = source_response.headers["Content-Type"]
    #             output_path = output_dir / f"{record.identifier}.{response_mime}"
    #             output_path.write_bytes(source_response.content)
    return result


def _parse_keywords(raw_keywords: typing.Optional[str]) -> typing.List[str]:
    if raw_keywords is not None:
        parsed = raw_keywords.split("&#13;")
        if parsed[0] == raw_keywords:
            parsed = raw_keywords.split("|")
            if parsed[0] == raw_keywords:
                parsed = raw_keywords.split(" ")
    else:
        parsed = []
    return [k for k in parsed if k != ""]


def compute_record_stats(records: typing.List[CswRecord]):
    result: typing.Dict = {"custodian": {}, "type": {}, "keywords": {}}
    for record in records:
        result["custodian"].setdefault(record.custodian, 0)
        result["custodian"][record.custodian] += 1
        result["type"].setdefault(record.type, 0)
        result["type"][record.type] += 1
        for keyword in record.keywords:
            result["keywords"].setdefault(keyword, 0)
            result["keywords"][keyword] += 1
    return result


def download_records_threaded_execution(
    url: str,
    execution_kwargs: typing.List[typing.Dict],
    num_workers: int,
    output_dir: Path,
) -> typing.List[typing.Dict]:
    errors = []
    with concurrent.futures.ThreadPoolExecutor(num_workers) as executor:
        to_do = {}
        for kwargs in execution_kwargs:
            future = executor.submit(download_records, url, **kwargs)
            to_do[future] = kwargs
        for i, future in enumerate(concurrent.futures.as_completed(to_do.keys())):
            kwargs = to_do[future]
            msg_prefix = f"({i + 1}/{len(to_do)}) - "
            try:
                page_records = future.result()
            except httpx.ReadTimeout:
                logger.exception(
                    f"{msg_prefix}Request timed out for {future}, " f"skipping..."
                )
                errors.append(kwargs)
            else:
                logger.info(f"{msg_prefix}Gotten results for {future}")
                save_records(page_records, CSW_NAMESPACES, output_dir)
    return errors


def retry_download_errors(
    url: str,
    execution_kwargs: typing.List[typing.Dict],
    max_workers: int,
    output_dir: Path,
    *,
    retry_number: int = 0,
    max_retries: int = 20,
) -> typing.List[typing.Dict]:
    num_workers = min(max_workers, len(execution_kwargs))
    errors = download_records_threaded_execution(
        url, execution_kwargs, num_workers, output_dir
    )
    if len(errors) > 0 and retry_number < max_retries:
        result = retry_download_errors(
            url, errors, max_workers, output_dir, retry_number=retry_number + 1
        )
    else:
        result = errors
    return result


def _retrieve_text(
    source: etree.Element,
    xpath_expression: str,
    namespaces: typing.Dict[str, str],
    *,
    is_multiple: bool = False,
):
    xpath_result = source.xpath(f"{xpath_expression}/text()", namespaces=namespaces)
    if is_multiple:
        result = xpath_result
    else:
        try:
            result = xpath_result[0]
        except IndexError:
            result = None
    return result


def _extract_record_identifier(
    record: etree.Element, *, namespaces: typing.Dict[str, str]
) -> typing.Optional[str]:
    try:
        id_ = record.xpath("dc:identifier/text()", namespaces=namespaces)[0]
    except IndexError:
        id_ = None
    else:
        raise
    finally:
        return id_


def _perform_get_records(
    url: str,
    render_context: typing.Dict,
    *,
    client: httpx.Client,
    xml_parser: etree.XMLParser,
) -> etree.Element:
    jinja_env = utils.get_jinja_env()
    template = jinja_env.get_template("legacy_sasdi_downloader/get_records.xml")
    request_body = template.render(**render_context)
    logger.debug(f"{request_body}")
    response = client.post(
        url, headers={"Content-Type": "text/xml"}, content=request_body.encode("utf-8")
    )
    response.raise_for_status()
    return etree.fromstring(response.content, parser=xml_parser)


def _get_num_records(
    get_records_response: etree.Element, *, namespaces: typing.Dict[str, str]
) -> typing.Optional[typing.Tuple[int, int]]:
    try:
        search_results_el = get_records_response.xpath(
            "csw:SearchResults", namespaces=namespaces
        )[0]
        matched = int(search_results_el.get("numberOfRecordsMatched", 0))
        returned = int(search_results_el.get("numberOfRecordsReturned", 0))
        result = (matched, returned)
    except IndexError:
        result = None
    return result
