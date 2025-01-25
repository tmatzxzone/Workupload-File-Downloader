import logging
import re
from tqdm import tqdm
from sys import argv, exit
from re import sub, search
from json import loads
from requests import get, Response

logging.root.name = "downloader"
logging.root.setLevel(logging.NOTSET)

valid_url = r'.*workupload.com/'
report_url = "https://github.com/knighthat/WorkuploadDownloader/issues"


def extract(url: str) -> dict:
    uri = sub(valid_url, '', url).split('/')

    logging.info(f"Download type: {uri[0]}")
    logging.info(f"File's id: {uri[1]}")

    return {
        'type': uri[0],
        'id': uri[1]
    }


def get_token(url: str) -> str:
    print(" ")
    logging.info("Getting token...")
    token = get(url, cookies=dict(token='')).cookies['token']
    logging.info(f"Your temporary token: {token}")
    return token


def get_download_url(parts: dict, headers: dict) -> str:
    print(" ")
    logging.info("Requesting download URL...")
    api_url = f"https://workupload.com/api/{parts['type']}/getDownloadServer/{parts['id']}"

    for attempt in range(3):
        data_response = get(api_url, headers=headers)
        logging.debug(f"Attempt {attempt + 1}: Status Code: {data_response.status_code}")
        if data_response.status_code == 200:
            break
        logging.warning(f"Failed to get a valid response. Retrying... ({attempt + 1}/3)")
        time.sleep(2)
    else:
        logging.error("Failed to get a valid response after 3 attempts.")
        raise ValueError("Failed to get a valid response.")

    try:
        logging.debug(f"API Response: {data_response.text}")
        json_data = loads(data_response.text)
        dl_url = json_data['data']['url']
        logging.info(f"Downloading from {dl_url}")
        return dl_url
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from response.")
        logging.error(f"Response content: {data_response.text}")
        raise
    except KeyError:
        logging.error("The response JSON does not contain the expected keys.")
        logging.error(f"Response content: {data_response.text}")
        raise



def get_file_information(url: str, headers: dict) -> dict:
    print(" ")
    logging.info("Searching file...")
    file_response = get(url, headers=headers, stream=True)

    name = file_response.headers.get('Content-Disposition')
    name = re.search(r'filename="(.+?)"', name).group(1)
    name = name.encode('latin1').decode('utf-8')  # Decode using UTF-8


    size = file_response.headers.get('Content-Length', 0)

    logging.info(f"File's name: {name}")
    logging.info(f"File's size: {size}")
    return {
        'name': name,
        'size': int(size),
        'response': file_response
    }


def download(name: str, size: int, response: Response) -> None:
    print(f"Downloading {name}...")
    progress_bar = tqdm(total=size, unit='iB', unit_scale=True)

    with open(name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                progress_bar.update(len(chunk))
                file.write(chunk)

    progress_bar.close()
    if size != 0 and progress_bar.n != size:
        logging.error(f"Error occurs during download. Report at \n {report_url}")


if __name__ == '__main__':
    if len(argv) < 2:
        logging.fatal("Usage: python main.py <url>")
        exit(1)

    link = argv[1]
    parts = extract(link)
    token = put token here bruh

    headers = {'Cookie': f'token={token}'}
    dl_url = get_download_url(parts, headers)

    content = get_file_information(dl_url, headers)

    download(content['name'], content['size'], content['response'])
