# Wenizit

## Install
```
  $ git clone https://github.com/katrina376/wenizit.git
  $ cd wenizit
  $ pip install -r requirements.txt
```
可以配合使用 virtualenv。

## Run
### 文件
```json
  {
    "title": （標題）,
    "content": （主文）,
    "commit_date": （日期，未選擇時為空白）,
  }
```
以 `*.json` 存放於 `data/` 內，並於 `list.txt` 中記錄文件檔名（不含副檔名）。

### 開始使用
```
  $ export FLASK_APP=application.py
  $ flask run
```
用瀏覽器打開 http://127.0.0.1:5000/<文件檔名>

## Use
1. 可以在畫面上選擇日期，於左側主文或右側清單上點選皆可。
2. 亦可以直接輸入日期。
3. 點選確認鈕。
4. 如果成功儲存，將會顯示下一個文件的連結。
