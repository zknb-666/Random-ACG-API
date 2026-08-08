import io

import requests
from PIL import Image


IMGLOC_UPLOAD_URL = 'https://imgloc.com/upload.php'
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
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


def optimize_image_for_upload(image_content, content_type, filename):
    if len(image_content) <= MAX_UPLOAD_SIZE:
        return filename, image_content, content_type

    try:
        image = Image.open(io.BytesIO(image_content))
        image_format = (image.format or '').upper()
        optimized_buffer = io.BytesIO()

        if image_format == 'PNG':
            image.save(optimized_buffer, format='PNG', optimize=True, compress_level=9)
            optimized_content_type = 'image/png'
            optimized_filename = filename.rsplit('.', 1)[0] + '.png'
        elif image_format == 'GIF':
            image.save(optimized_buffer, format='GIF', optimize=True)
            optimized_content_type = 'image/gif'
            optimized_filename = filename.rsplit('.', 1)[0] + '.gif'
        elif image_format in ('JPEG', 'JPG'):
            image = image.convert('RGB')
            image.save(
                optimized_buffer,
                format='JPEG',
                optimize=True,
                progressive=True,
                quality='keep',
                subsampling='keep',
            )
            optimized_content_type = 'image/jpeg'
            optimized_filename = filename.rsplit('.', 1)[0] + '.jpg'
        else:
            return filename, image_content, content_type

        optimized_content = optimized_buffer.getvalue()
        if optimized_content and len(optimized_content) <= len(image_content):
            return optimized_filename, optimized_content, optimized_content_type

        return filename, image_content, content_type
    except Exception:
        return filename, image_content, content_type


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
    filename, image_content, content_type = optimize_image_for_upload(image_content, content_type, filename)
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