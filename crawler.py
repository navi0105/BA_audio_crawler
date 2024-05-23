import os
import argparse
from pathlib import Path
import shutil
import tempfile
from tqdm import tqdm

from utils.utils import ( 
    crawl_from_url,
    process_wav
)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--url', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, default='output/')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    url = args.url

    name, result = crawl_from_url(url)
    print("Student Name:", name)

    # make output dir
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    # make tempdir
    tempdir = tempfile.mkdtemp()
    # download and process audio files
    try:
        metadata = []
        for audio_url, text in tqdm(result):
            output_audio_path = process_wav(audio_url, tempdir, outdir)
            metadata.append(f"{output_audio_path}|{text.strip()}")
    finally:
        # remove tempdir
        shutil.rmtree(tempdir)

    # save metadata
    with open(outdir / 'metadata.txt', 'w') as f:
        f.write('\n'.join(metadata))


if __name__ == '__main__':
    main()