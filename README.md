# Blue Archive Wiki Character Audio Crawler
一個簡單的爬蟲程式，可以在 [Blue Archive 簡中 Wiki]() 上爬取所有已實裝角色 (含合作角) + 部分 NPC / 未實裝角色之語音及文本。

## Requirement
- Python >= 3.8
- ffmpeg
### Install Python packages
```
pip install -r requirements.txt
```

## Usage
### Crawl All Data
直接執行 `crawl_all.py` 即可開始全實裝角色的語音 (含文本) 資料抓取
```
python crawl_all.py -o <output_directory>
```

#### About crawled data
使用 `crawl_all.py` 爬取所有音檔後之資料夾架構如下:
```
<output_directory>
├── metadata.txt
└── wavs
    ├── 伊落マリー_170297
    ├── 小塗マキ_67654
    ├── 下江コハル_595927
    ├── ...
    └── 明星ヒマリ_575949
```
`metadata.txt` 記錄了所有語音檔的檔案位置及其對應文本，加以處理的話可嘗試應用在 TTS / VC / SVC 等深度學習任務上。

`wavs/` 存放了所有角色的語音檔，以角色爲單位儲存，子資料夾的命名規則目前爲 `<角色名字>_<角色在 Wiki 上的編號>`，角色名字以程式在 Wiki 上爬到的全名爲準，角色的 Wiki 編號則是他們在撰寫 Wiki 期間給每個角色 (或是說分頁) 分配到的編號。例如禮服陽奈的編號是 611753，那他在 Wiki 對應的 URL 就是 https://www.gamekee.com/ba/611753.html

> 註1: 使用目前的命名規則的原因是目前中文 Wiki 對角色的命名定義不太統一 (例: [原版小春](https://www.gamekee.com/ba/78300.html) 和 [泳裝小春](https://www.gamekee.com/ba/595927.html) 在 Wiki 上標記的名字都是一樣的; [正月茜香](https://www.gamekee.com/ba/150380.html) 姓氏的平假名讀音擺放位置和 [原版](https://www.gamekee.com/ba/46678.html)不一樣)，在

### Crawl Single Character
如果只想抓取特定角色 / NPC / 未實裝 (但已有語音資料) 角色的話可以利用 `crawler.py` 進行單一角色的語音 (含文本) 資料抓取
```bash
python crawler.py -u <url> -o <output_directory>

# Example
# 以抓取 ヒナ（ドレス）爲例
# url = "https://www.gamekee.com/ba/611753.html"
# python crawler.py -u https://www.gamekee.com/ba/611753.html -o ./hina_dress
```
> 註2: NPC 和未實裝角色的資料抓取目前還沒全數實測，語音資料有高機率爬不到 / 爬錯，還請注意。

> 註3: 百合園聖亞的語音資料目前 (2024 / 05 / 23) 還抓不到，相當遺憾。

## TODO
TBD.