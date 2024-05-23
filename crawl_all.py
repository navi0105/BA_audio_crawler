import os
import argparse
from pathlib import Path
import shutil
import tempfile
import requests
from lxml import etree
from tqdm import tqdm

from utils.utils import (
    crawl_from_url,
    process_wav
)

WIKI_URL = 'https://www.gamekee.com/ba/'
CHARACTER_TABLE_XPATH = '//*[@id="menu-23941"]/div[3]/div[2]/div[1]/div[2]/a'

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output', type=str, default='ba_audios/')

    args = parser.parse_args()
    return args

def get_character_urls(url):
    """
        Get character urls from the given url

        Args:
            url (str): url of the character list page
        
        Returns:
            character_url_info: a list of tuples, each tuple contains character id (for wiki pages) and url
    """

    response = requests.get(url)
    content = response.content.decode()
    html = etree.HTML(content)
    tree = etree.ElementTree(html)

    character_elements = tree.xpath(CHARACTER_TABLE_XPATH)
    character_urls = [element.attrib['href'] for element in character_elements]

    for i, character_url in enumerate(character_urls):
        character_urls[i] = WIKI_URL + character_url[4: ]
    
    character_url_info = []
    for character_url in character_urls:
        character_url = character_url.strip()
        url_id = os.path.basename(character_url).split('.')[0]
        character_url_info.append((url_id, character_url))

    return character_url_info

def main():
    args = parse_args()

    print("Getting character urls...")
    character_url_info = get_character_urls(WIKI_URL)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Crawling audio files...")
    tempdir = tempfile.mkdtemp()
    metadata = []
    try:
        for url_id, url in character_url_info:
            name, result = crawl_from_url(url)
            print(f"Student Name: {name}")
            print(f"Url: {url}")

            wavdir = output_dir / 'wavs' / f'{name}_{url_id}'
            if wavdir.exists():
                print(f"{name}_{url_id} already exists, skipping...")
                continue

            wavdir.mkdir(parents=True, exist_ok=True)
            for audio_url, text in tqdm(result):
                output_audio_path = process_wav(audio_url, tempdir, wavdir)
                metadata.append(f"{name}_{url_id}|{output_audio_path}|{text.strip()}")
                
    except Exception as e:
        print(e)
    finally:
        shutil.rmtree(tempdir)

    with open(output_dir / 'metadata.txt', 'w') as f:
        f.write('\n'.join(metadata))

    print("Done!")

if __name__ == "__main__":
    main()