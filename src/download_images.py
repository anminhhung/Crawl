import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse

"""
Checks whether `url` is a valid URL.
"""
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

"""
Returns all image URLs on a single `url`
"""
def get_all_images(url):
    soup = bs(requests.get(url).content, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)
        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    return urls

"""
Downloads a file given an URL and puts it in the folder `pathname`
"""
def download(url, pathname):
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.umask(0)
        os.makedirs(pathname, mode=0o777)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])
    print("URL: ", url)
    print("filename: ", filename)
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    try:
        with open(filename, "wb") as f:
            for data in progress:
                # write data read to the file
                f.write(data)
                # update the progress bar manually
                progress.update(len(data))
    except IsADirectoryError as e:
        print(e)
        pass


def crawling(url, path="crawl_dir"):
    # get all images
    raw_dir = "download"
    if not os.path.exists(raw_dir):
        os.umask(0)
        os.makedirs(raw_dir, mode=0o777)

    if not os.path.isdir(path):
        os.umask(0)
        os.makedirs(path, mode=0o777)

    name_dir = len(next(os.walk(raw_dir))[1])
    path = os.path.join(path, str(name_dir))
    imgs = get_all_images(url)
    for img in imgs:
        # for each img, download it
        download(img, path)


# if __name__ == "__main__":
#     url = "http://introtodeeplearning.com/?fbclid=IwAR27XRKrDKguKZnsc4EBT6GuRF7qsEqkAPHHq108t912y97DJ08fj44zT9I"
#     path = "web-scaping"
#     crawling(url)