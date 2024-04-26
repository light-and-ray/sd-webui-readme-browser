import os, hashlib, time
import urllib.request 
from threading import Thread
from readme_browser.options import getCacheLocation


def needCacheURL(url: str):
    if 'github.com' in url and '/assets/' in url:
        return True
    if 'githubusercontent.com' in url:
        return True
    if 'i.imgur.com' in url:
        return True
    return False


def cache(url: str, extName: str) -> str|None:
    if '?' in url:
        url = url.removesuffix('?' + url.split('?')[-1])
    if not needCacheURL(url):
        return None

    cachedFile = None

    try:
        name = url.split('/')[-1]
        dirHash = hashlib.md5(url.removesuffix(name).encode('utf-8')).hexdigest()[:6]
        outPath = os.path.join(getCacheLocation(), extName, dirHash, name)
        os.makedirs(os.path.dirname(outPath), exist_ok=True)
        if os.path.exists(outPath):
            cachedFile = outPath
        else:
            def func():
                try:
                    time.sleep(1)
                    urllib.request.urlretrieve(url, outPath)
                    print(f'readme_browser cached file {url}')
                except Exception as e:
                    # print(f'Error while caching file {url}, extName = {extName}')
                    # print(e)
                    pass
            Thread(target=func).start()

    except Exception as e:
        print(f'Error while caching file {url}, extName = {extName}')
        print(e)

    return cachedFile

