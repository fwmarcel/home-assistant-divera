def remove_accesskey(url):
    urlStr: str = str(url)
    return urlStr[:urlStr.find('?')]
