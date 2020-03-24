# Flashscore scraper
An application to gather data about archival scores and tables from [Flashscore](https://www.flashscore.com). It scrapes the data using chosen web browser (Firefox or Chrome) and puts them into the database with following structure:
![scraper_erd](https://user-images.githubusercontent.com/33002299/77449098-d9fcf100-6df1-11ea-9996-dd79a8214a72.png)
## Installation
Use `pip` to install required modules.
```
pip install requirements.txt
```
## Usage
Use `python` to run the scraper
```
python scrape.py
```
with following arguments:
| Short | Long    | Required | Value |
| -- | ---------- | -------- | ------ |
| -s | -\-os      | yes      | operating system: linux or windows |
| -b | -\-browser | yes      | browser used to scraping data: chrome or firefox |
| -l | -\-leagues | yes      | countries names; currently supported countries are listed in help |
| -h | -\-help    | no       | shows parameters description and list of their available values |
### Usage example
```
python scrape.py -s windows -b chrome -l England Italy Netherlands
```