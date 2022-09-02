function maxLengthCheck(object) {
    if (object.value.length > object.maxLength) {
        object.value = object.value.slice(0, object.maxLength)
    }
}

function getUrlParameter(param) {
    let sPageURL = window.location.search.substring(1),
        URLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < URLVariables.length; i++) {
        sParameterName = URLVariables[i].split('=');
        if (sParameterName[0] === param) {
            return sParameterName[1];
        }
    }
    return false;
}

function removeParameter(key, url) {
    let returnURL = url.split("?")[0],
        parameter,
        parameters_arr = [],
        queryString = (url.indexOf("?") !== -1) ? url.split("?")[1] : "";
    if (queryString !== "") {
        parameters_arr = queryString.split("&");
        for (let i = parameters_arr.length - 1; i >= 0; i -= 1) {
            parameter = parameters_arr[i].split("=")[0];
            if (parameter === key) {
                parameters_arr.splice(i, 1);
            }
        }
        if (parameters_arr.length) returnURL = returnURL + "?" + parameters_arr.join("&");
    }
    return returnURL;

}
