import re


def getURLsFromFile(file: str) -> list[str]:
    urls = []

    MDLinks = re.findall(r'\[.*?\]\(.+?\)', file)
    for link in MDLinks:
        tmp: str = link.replace(r'\(', '')
        tmp = link.split('(')[-1]
        url = tmp.removesuffix(')')
        urls.append(url)

    srcLinks = re.findall(r'src=".+?"', file)
    for link in srcLinks:
        url = link.split('"')[-2]
        urls.append(url)

    hrefLinks = re.findall(r'href=".+?"', file)
    for link in hrefLinks:
        url = link.split('"')[-2]
        urls.append(url)

    return urls


def isLocalURL(url: str):
    return '://' not in url


def isAnchor(url: str):
    return url.startswith('#')

def isMarkdown(url: str):
    if '#' in url:
        url = url.removesuffix(url.split('#')[-1])
    return url.endswith('.md')
