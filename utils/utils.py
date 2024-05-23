import os
import re
import wget
from typing import Union
import requests
import subprocess
from lxml import etree
from pathlib import Path
import pdb


def replace_audio_url(url: str):
    url = url.replace('//', 'https://')
    return url    

def convert_to_wav(input_path: str, output_path: str):
    assert output_path.endswith('.wav'), f"{output_path} does not end with .wav"
    subprocess.run(['ffmpeg', '-i', input_path, output_path, '-hide_banner', '-loglevel', 'error'])

def process_wav(audio_url: str, tempdir: Path, outdir: Path):
    """
        Download audio file and convert it to wav format

        Args:
            audio_url (str): url of the audio
            tempdir (Path): temporary directory to store the downloaded audio file
            outdir (Path): output directory to store the converted wav file
    
        Returns:
            output_audio_path (str): path of the converted wav file
    """
    
    temp_audio_path = wget.download(audio_url, out=tempdir)
    audio_name = os.path.basename(temp_audio_path)[: -4] + '.wav'
    output_audio_path = str(outdir / audio_name)

    # convert ogg/mp3 to wav
    convert_to_wav(temp_audio_path, output_audio_path)
    return output_audio_path

def process_name(tree: etree._Element):
    name_element = tree.xpath('.//span[text()="全名"]')[0]
    while name_element.tag != 'tr':
        name_element = name_element.getparent()

    name_element = name_element.xpath('.//td')[1]
    name = ''.join(name_element.itertext())
    # 移除部分角色姓氏上的平假名
    # TODO: Find a more general way to remove hiragana on Kanji
    hiragana = name_element.xpath('.//span[@style="font-size: 12px;" or @style="font-size: 14px;"]')
    for h in hiragana:
        h_text = ''.join(h.itertext())
        if h_text != name: # 目前的抓法會導致 里浜 ウミカ 的名字整個被移除，應急處理用
            name = re.sub(h_text, '', name, 1)
    name = name.strip().replace(' ', '')
    return name

def get_text_from_element(element: etree._Element):
    text = ''.join(element.itertext())

    # remove text in <section>
    section = element.xpath('.//section')
    section_text = ''.join([s.text for s in section])
    text = text.replace(section_text, '')

    return text

def crawl_from_url(url: str):
    """
        Crawl character's audio and text from the given url

        Args:
            url (str): url of the character's page
        
        Returns:
            id: student name
            data_pair: list of tuples, each tuple contains audio url and text
    """

    response = requests.get(url)
    content = response.content.decode()
    html = etree.HTML(content)
    tree = etree.ElementTree(html)

    # get student name
    name = process_name(tree)

    # get audio url
    audio_responses = tree.findall('.//audio')
    audio_elements = []
    audio_urls = []

    for element in audio_responses:
        temp = element
        while True:
            if temp is None:
                break
            if (temp.tag == 'div') and (temp.attrib.get('data-index') is not None):
                break
            temp = temp.getparent()

        # 1 => Jpanaese, 2 / 3 => Chinese
        # 中文版資料不齊全，只取日文版
        # temp == None => 還沒有中文版
        if temp is None:
            audio_elements.append(element)
            audio_url = element.attrib['src']
            audio_urls.append(audio_url)
        elif temp.attrib.get('data-index') == '1':
            audio_elements.append(element)
            audio_url = element.attrib['src']
            audio_urls.append(audio_url)
             
    
    # get text based on audio's xpath
    text_elements = []
    for element in audio_elements:
        parent = element.getparent()
        while parent.tag != 'tr':
            parent = parent.getparent()

        parent_path = tree.getpath(parent)
        text_xpath = parent_path + '/td'
        text_elements.append(tree.xpath(text_xpath)[-1])

    texts = [get_text_from_element(e) for e in text_elements]

    assert len(audio_urls) == len(texts), f"{len(audio_urls)} != {len(texts)}"

    for i in range(len(audio_urls)):
        audio_urls[i] = replace_audio_url(audio_urls[i])

    return name, list(zip(audio_urls, texts))