import uuid


def handle_named_url(data_dict: dict):
    """
    adding uuid to the named url
    , the name field was a bit
    confusing to the client.
    """
    title = data_dict.get("title")
    name = _remove_special_characters_from_package_url(title)
    if name is not None:
        name = name.replace(" ", "-")
        name += "-" + str(uuid.uuid4())
        name = name.lower()
        return name


def _remove_special_characters_from_package_url(url):
    """
    special characters are not
    accepted by CKAN for dataset
    urls, replace them
    """
    special_chars = "!\"”'#$%&'()*+,-./:;<=>?@[\]^`{|}~.[]"
    if url is not None:
        for i in url:
            if i in special_chars:
                url = url.replace(i, "-")

        return url
