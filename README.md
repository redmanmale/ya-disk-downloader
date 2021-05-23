# Ya.Disk Downloader

Python3 script to download files from shared Yandex.Disk folder without account.

## How to use

downloader.py URL Folder-to-save [optional regex to filter files]


## Prerequisites

* Python3


## Limitations

* No error handling
* Regex is applied only to files, not folders


## Improvements relative to the base version

* Nested folders are supported: folder structure is mirrored to destination
* Regex is truly optional now
* Script is now compatible with beautifulsoup4 4.9.0+


## Disclaimer

I made the changes in pursuit of a practical goal and then decided to share them. It works, but code structure has suffered a bit. There is still space for improvements, but for now I'm not planning to work on this.
