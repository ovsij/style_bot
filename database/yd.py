import httplib2
import json
import requests
from urllib.parse import urlencode

async def download_image(url, path):
    # Получаем загрузочную ссылку
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    final_url = base_url + urlencode(dict(public_key=url))
    h = httplib2.Http('.cache')
    response, content = h.request(final_url)
    download_url = json.loads(content.decode('utf-8'))['href']
    # Загружаем файл и сохраняем его
    response, content = h.request(download_url)
    with open(path, 'wb') as f:   # Здесь укажите нужный путь к файлу
        f.write(content)
    
