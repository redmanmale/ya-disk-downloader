import json
import os
import shutil
import sys
from os import path
from urllib import parse

import regex as regex
import requests
from bs4 import BeautifulSoup


class FileList:
    def __init__(self, files, sk, cookie):
        self.files = files
        self.sk = sk
        self.cookie = cookie


def filter_file(file_filter, filename):
    if file_filter is None:
        return True

    return regex.search(file_filter, filename, regex.IGNORECASE)


def fetch_files(fetch_hash, offset, sk, cookie, file_filter, files_to_download):
    """
    Fetch the rest of the files in folder
    """

    params = json.dumps({"hash": fetch_hash, "offset": offset, "sk": sk})
    headers = {"Content-Type": "text/plain", "Host": "yadi.sk", "Cookie": cookie}
    data = parse.quote(params).encode()

    file_url_resp = requests.post("https://yadi.sk/public/api/fetch-list", data=data, headers=headers)
    file_url_raw = file_url_resp.json()

    resources = file_url_raw["resources"]

    for file in resources:
        if file["type"] != "dir":
            match = filter_file(file_filter, file["name"])
            if match:
                files_to_download.append(file["path"])

    return resources[0]["completed"], len(resources)


def get_files_list(url, file_filter):
    """
    Get list of files in folder filtered with regex
    """

    get_files_resp = requests.get(url)
    cookie = get_files_resp.headers["Set-Cookie"]

    get_files_raw = get_files_resp.content
    get_files_html = BeautifulSoup(get_files_raw, 'html.parser')

    get_files_json_raw = get_files_html.find("script", {"id": "store-prefetch"})
    get_files_json = json.loads(get_files_json_raw.get_text())

    sk = get_files_json["environment"]["sk"]

    root_resource_id = get_files_json["rootResourceId"]
    resources = get_files_json["resources"]
    root = resources[root_resource_id]
    files = root["children"]
    fetch_hash = root["hash"]

    files_to_download = []
    offset = 0
    for file_id in files:
        file = resources[file_id]["path"]
        match = filter_file(file_filter, file)
        offset += 1
        if match:
            files_to_download.append(file)

    completed = root["completed"]
    while not completed:
        completed, new_offset = fetch_files(fetch_hash, offset, sk, cookie, file_filter, files_to_download)
        offset += new_offset

    print("Got " + str(len(files_to_download)) + " files matching filter: " + file_filter)

    return FileList(files_to_download, sk, cookie)


def download_file(url, filename):
    """
    Download file from url and save it
    """

    if path.exists(filename):
        return

    with requests.get(url, stream=True) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def get_file_url(file, sk, cookie, folder):
    """
    Get direct file url from its ID
    """

    filename = file[file.find(":/") + 2:]
    params = json.dumps({"hash": file, "sk": sk})
    headers = {"Content-Type": "text/plain", "Host": "yadi.sk", "Cookie": cookie}
    data = parse.quote(params).encode()

    file_url_resp = requests.post("https://yadi.sk/public/api/download-url", data=data, headers=headers)
    file_url_raw = file_url_resp.json()
    file_url = file_url_raw["data"]["url"]

    download_file(file_url, os.path.join(folder, filename))


def main(url, folder, file_filter):
    if not path.exists(folder):
        os.mkdir(folder)

    file_list = get_files_list(url, file_filter)

    counter = 0
    count = len(file_list.files)
    for file in file_list.files:
        get_file_url(file, file_list.sk, file_list.cookie, folder)
        counter += 1
        print(str(counter) + "/" + str(count))

    print("Done.")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
