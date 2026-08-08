import requests


IMGLOC_UPLOAD_URL = 'https://imgloc.com/upload.php'
WALLHAVEN_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'
}


def get_wallhaven_image(session, img_url):
    x = img_url.split('/')[-1]
    a = x[0] + x[1]
    base_img_url = 'https://w.wallhaven.cc/full/' + a + '/wallhaven-' + x
    for format in ('.jpg', '.png'):
        real_url = base_img_url + format
        response = session.get(url=real_url, headers=WALLHAVEN_HEADERS, timeout=60, verify=False)
        if response.ok:
            content_type = response.headers.get('Content-Type', 'image/jpeg').split(';')[0] or 'image/jpeg'
            return real_url, response.content, content_type
    raise RuntimeError('无法获取原图:' + base_img_url)


def get_imgloc_token(session):
    response = session.get(IMGLOC_UPLOAD_URL, params={'action': 'token'}, headers=WALLHAVEN_HEADERS, timeout=60, verify=False)
    response.raise_for_status()
    data = response.json()
    if not data.get('ok') or not data.get('token'):
        raise RuntimeError(data.get('message', '无法获取上传凭证'))
    return data['token']


def upload_to_imgloc(session, image_url, image_content, content_type):
    token = get_imgloc_token(session)
    filename = image_url.split('/')[-1]
    files = {'image': (filename, image_content, content_type)}
    data = {'token': token}
    response = session.post(IMGLOC_UPLOAD_URL, headers=WALLHAVEN_HEADERS, files=files, data=data, timeout=120, verify=False)
    response.raise_for_status()
    result = response.json()
    if not result.get('ok') or not result.get('url'):
        raise RuntimeError(result.get('message', '上传失败'))
    return result['url']


def upload_wallhaven_images_to_txt(img_url_list, filename, label):
    with open(filename, 'w', encoding='utf-8') as randimgs:
        with requests.Session() as session:
            for img_url in img_url_list:
                try:
                    source_url, image_content, content_type = get_wallhaven_image(session, img_url)
                    img_loc_url = upload_to_imgloc(session, source_url, image_content, content_type)
                    randimgs.write(img_loc_url + '\n')
                    print(label + '链接:\n' + str(img_loc_url) + '\n获取完成\n')
                except Exception as exc:
                    print('上传失败:\n' + str(img_url) + '\n原因: ' + str(exc) + '\n')