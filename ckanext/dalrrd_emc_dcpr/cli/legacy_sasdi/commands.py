import concurrent.futures
import logging
import re
import typing
from concurrent import futures
from pathlib import Path

import click
import httpx
from ckan.plugins import toolkit
from lxml import etree

from .. import _CkanEmcDataset, utils

from .import_mappings import CUSTODIAN_MAP, IMPORT_TAG_NAME, get_owner_org
from .csw import csw_downloader
from .saeon_odp import importer as saeon_importer

logger = logging.getLogger(__name__)

_xml_parser = etree.XMLParser(resolve_entities=False)

_DEFAULT_LEGACY_SASDI_RECORD_DIR = (
    Path.home() / "data/storage/legacy_sasdi_downloader/csw_records"
)
_DEFAULT_LEGACY_SASDI_THUMBNAIL_DIR = (
    Path.home() / "data/storage/legacy_sasdi_downloader/thumbnails"
)
_DEFAULTS_SAEON_ODP_RECORDS_DIR = (
    Path.home() / "data/storage/legacy_sasdi_downloader/saeon_odp_records"
)

_DEFAULT_MAX_WORKERS = 5


@click.group()
@click.option("--verbose", is_flag=True)
def legacy_sasdi(verbose: bool):
    """Commands that deal with import of catalog records from the legacy SASDI"""
    click_handler = utils.ClickLoggingHandler()
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO, handlers=(click_handler,)
    )


@legacy_sasdi.group()
def saeon_odp():
    """Commands that rely on the SAEON-ODP platform."""


@legacy_sasdi.group()
def csw():
    """Commands that rely on the CSW interface to the legacy SASDI"""


@csw.command()
@click.option(
    "--url",
    default="http://app01.saeon.ac.za/PLATFORM_TEST/MAP/csw.asp",
    show_default=True,
    help="Legacy SASDI CSW endpoint",
)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.option(
    "--output-dir",
    type=click.types.Path(),
    default=_DEFAULT_LEGACY_SASDI_RECORD_DIR,
    show_default=True,
)
@click.option(
    "--max-workers", type=int, default=_DEFAULT_MAX_WORKERS, show_default=True
)
def download_records(url: str, page_size: int, output_dir: Path, max_workers):
    """download catalogue records from the legacy SASDI

    Uses the legacy SASDI CSW interface to retrieve existing catalogue records with
    the csw:Record typename.

    """

    with httpx.Client() as client:
        try:
            total_records = csw_downloader.find_total_records(
                url, client=client, xml_parser=_xml_parser
            )
            logger.debug(f"{total_records=}")
        except httpx.ConnectError:
            logger.exception(msg=f"Could not connect to {url!r}")
        except httpx.ReadTimeout:
            logger.exception(msg=f"Connection timed out {url!r}")
        else:
            total = total_records or 0
            if total > 0:
                num_pages, remainder = divmod(total, page_size)
                if remainder > 0:
                    num_pages += 1
                logger.debug(f"{num_pages=}")
                execution_kwargs = []
                for page in range(num_pages):
                    kwargs = {
                        "limit": page_size,
                        "offset": (page * page_size),
                        "client": client,
                        "xml_parser": _xml_parser,
                    }
                    execution_kwargs.append(kwargs)
                workers = min(max_workers, num_pages)
                errors = csw_downloader.download_records_threaded_execution(
                    url, execution_kwargs, workers, output_dir
                )
                if len(errors) > 0:
                    logger.warning(f"{len(errors)} pages failed, retrying...")
                    final_errors = csw_downloader.retry_download_errors(
                        url, errors, max_workers, output_dir
                    )
                    if len(final_errors) > 0:
                        logger.warning(
                            f"Got {len(final_errors)} final errors, after retrying. "
                            f"Could not fetch all pages"
                        )
            else:
                logger.warning(
                    f"Could not find any records on CSW catalogue at {url!r}"
                )


@csw.command()
@click.option(
    "--records-dir",
    type=click.types.Path(),
    default=_DEFAULT_LEGACY_SASDI_RECORD_DIR,
    show_default=True,
)
@click.option(
    "--output-dir",
    type=click.types.Path(),
    default=_DEFAULT_LEGACY_SASDI_THUMBNAIL_DIR,
    show_default=True,
)
@click.option(
    "--max-workers", type=int, default=_DEFAULT_MAX_WORKERS, show_default=True
)
def retrieve_thumbnails(records_dir: Path, output_dir: Path, max_workers: int):
    """Retrieve thumbnails for previously downloaded legacy SASDI records"""
    num_retrieved = 0
    page_size = 10
    with httpx.Client() as client:
        batch = []
        for idx, path in enumerate(records_dir.iterdir()):
            logger.debug(f"({idx + 1}) Processing path {path!r}...")
            if path.is_file():
                record = csw_downloader.parse_record(
                    path,
                    csw_downloader.CSW_NAMESPACES,
                    xml_parser=_xml_parser,
                )
                batch.append(record)
            if len(batch) == page_size:
                downloaded_paths = _concurrent_thumbnail_download(
                    batch, output_dir, client=client, num_workers=max_workers
                )
                num_retrieved += len(downloaded_paths)
                batch = []
        else:  # download last ones
            downloaded_paths = _concurrent_thumbnail_download(
                batch, output_dir, client=client, num_workers=max_workers
            )
            num_retrieved += len(downloaded_paths)
    logger.info(f"Retrieved {num_retrieved} thumbnails")


@csw.command("import-records")
@click.option(
    "--records-dir",
    type=click.types.Path(),
    default=_DEFAULT_LEGACY_SASDI_RECORD_DIR,
    show_default=True,
)
@click.option(
    "--thumbnails-dir",
    type=click.types.Path(),
    default=_DEFAULT_LEGACY_SASDI_THUMBNAIL_DIR,
    show_default=True,
)
def import_records_csw(records_dir: Path, thumbnails_dir: Path):
    """Import previously downloaded legacy SASDI records into the EMC"""
    seen_orgs: typing.Dict[str, typing.Dict] = {}
    for item in (i for i in records_dir.iterdir() if i.is_file()):
        record = csw_downloader.parse_record(
            item, csw_downloader.CSW_NAMESPACES, xml_parser=_xml_parser
        )
        target_org = get_owner_org(record.custodian)
        if target_org is None:
            pass  # this will be imported into the unsorted org
        elif target_org not in seen_orgs.keys():
            organization, _ = utils.maybe_create_organization(target_org)
            seen_orgs[organization["name"]] = organization
        else:
            organization = seen_orgs[target_org]
        owner_user = None
    logger.error("Not implemented yet")


@saeon_odp.command("import-records")
@click.option(
    "--records-dir",
    type=click.types.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    default=_DEFAULTS_SAEON_ODP_RECORDS_DIR,
    show_default=True,
)
@click.pass_context
def import_records_saeon_odp(ctx, records_dir: Path):
    seen_names: typing.Set[str] = set()
    flask_app = ctx.meta["flask_app"]
    with flask_app.test_request_context():
        for idx, path in enumerate(p for p in records_dir.iterdir() if p.is_file()):
            parsed_record = saeon_importer.parse_record(path)
            fixed_name = _fix_name(parsed_record.name, seen_names)
            seen_names.add(fixed_name)
            parsed_record.name = fixed_name
            org_name = parsed_record.owner_org
            owner_org, _ = utils.maybe_create_organization(
                org_name,
                title=CUSTODIAN_MAP[org_name].get("title"),
                description=CUSTODIAN_MAP[org_name].get("description"),
            )
            logger.debug(f"({idx}) - Creating {parsed_record.name!r}...")
            org_admin = [
                u for u in owner_org.get("users", []) if u["capacity"] == "admin"
            ][0]
            data_dict = parsed_record.to_data_dict()
            utils.create_single_dataset(org_admin, data_dict)
    logger.info("Done!")


@saeon_odp.command()
@click.option("--page-size", type=int, default=10)
@click.pass_context
def purge_imported_records(ctx, page_size: int):
    """Delete imported records

    Imported records are found by the presence of a specially named tag.

    """

    flask_app = ctx.meta["flask_app"]
    with flask_app.test_request_context():
        get_number_result = toolkit.get_action("package_search")(
            context={"ignore_auth": True},
            data_dict={
                "include_private": True,
                "fq": f"tags:{IMPORT_TAG_NAME}",
                "rows": 0,
            },
        )
    num_datasets = get_number_result.get("count")
    if num_datasets is not None and num_datasets > 0:
        num_pages, remainder = divmod(num_datasets, page_size)
        num_pages = num_pages + 1 if remainder > 0 else num_pages
        num_done = 0
        for page in reversed(range(num_pages)):
            with flask_app.test_request_context():
                get_datasets_result = toolkit.get_action("package_search")(
                    context={"ignore_auth": True},
                    data_dict={
                        "include_private": True,
                        "fq": f"tags:{IMPORT_TAG_NAME}",
                        "start": page * page_size,
                        "rows": page_size,
                    },
                )
            datasets = get_datasets_result.get("results", [])
            for dataset in datasets:
                logger.info(
                    f"({num_done + 1}/{num_datasets}) Deleting dataset {dataset.get('id')}..."
                )
                with flask_app.test_request_context():
                    toolkit.get_action("dataset_purge")(
                        context={"ignore_auth": True}, data_dict={"id": dataset["id"]}
                    )
                    num_done += 1
        logger.info("Done!")
    elif num_datasets == 0:
        logger.info(f"There are no datasets to delete")
        logger.info("Done!")
    else:
        logger.error(f"Could not determine number of imported datasets")


def _concurrent_thumbnail_download(
    records: typing.List[csw_downloader.CswRecord],
    output_dir: Path,
    *,
    client: httpx.Client,
    num_workers: int,
) -> typing.List[Path]:
    """Download and save thumbnails using concurrent techniques"""
    result = []
    with futures.ThreadPoolExecutor(num_workers) as executor:
        to_do = {}
        for record in records:
            future = executor.submit(
                csw_downloader.retrieve_thumbnail,
                record,
                output_dir,
                client=client,
            )
            to_do[future] = record
        for future in futures.as_completed(to_do.keys()):
            record = to_do[future]
            try:
                thumbnail_path = future.result()
            except httpx.ReadTimeout:
                logger.exception(
                    f"Request timed out for {record.identifier!r}, skipping..."
                )
            else:
                if thumbnail_path is not None:
                    logger.info(f"Gotten {thumbnail_path!r}")
                    result.append(thumbnail_path)
    return result


def _generate_new_name(name: str, max_name_len: int) -> str:
    """Generates a new name by PREFIXING a numeric string"""
    pattern = re.compile(r"^(\d+)-")
    max_len = max_name_len - 2
    has_number = pattern.search(name)
    if has_number:
        current = int(has_number.group(1))
        next_ = str(current + 1)
        if len(name) >= max_len:
            if len(next_) > len(str(current)):
                # the next number occupies one more char than the previous one, we
                # need to make space for it. We do it by removing a char at the end of
                # the name
                new_name = pattern.sub(f"{next_}-", name[:-1])
            else:
                new_name = pattern.sub(f"{next_}-", name)
        else:
            new_name = pattern.sub(f"{next_}-", name)
    else:
        if len(name) >= max_len:
            new_name = "1-" + name[:-2]
        else:
            new_name = "1-" + name
    return new_name


def _fix_name(
    name: str,
    seen_names: typing.Iterable[str],
    *,
    max_name_len: int = 100,
) -> str:
    """Fix duplicate names by appending a number to them

    This function tries to come up with unique names. If the input `name` is present
    in the `seen_names` iterable, then a new name will be derived from the input one.
    The new name will not have a larger length than the input `max_name_len`

    New names are generated by suffixing a slash and an increasing number to the end
    of the input `name`. When the original name is too big, this function chops off
    characters from the non-suffix part.

    """

    if name in seen_names:
        new_name = _generate_new_name(name, max_name_len)
        result = _fix_name(new_name, seen_names, max_name_len=max_name_len)
    else:
        result = name
    return result
