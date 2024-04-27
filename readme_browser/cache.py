import os, hashlib, time
import urllib.request 
from threading import Thread
from readme_browser.options import getCacheLocation

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

ALLOWED_EXTENSIONS = ['.jpeg', '.jpg', '.png', '.webp', '.gif', '.mp4', '.webm']

def needCacheURL(url: str):
    url = url.lower()
    hasAllowedExt = any(url.endswith(x) for x in ALLOWED_EXTENSIONS)

    if 'github.com' in url and '/assets/' in url:
        return True
    if 'github.com' in url and '/blob/' in url and hasAllowedExt:
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
                    nonlocal url
                    time.sleep(1)
                    url += '?raw=true'
                    urllib.request.urlretrieve(url, outPath)
                    print(f'readme_browser cached file {url}, extName = {extName}')
                except Exception as e:
                    # print(e)
                    pass
            Thread(target=func).start()

    except Exception as e:
        print(f'Error while caching file {url}, extName = {extName}')
        print(e)

    return cachedFile

