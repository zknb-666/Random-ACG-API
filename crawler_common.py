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

        def encode_jpeg_under_limit(source_image):
            working_image = source_image.convert('RGB')
            width, height = working_image.size
            scale_steps = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3)
            quality_steps = (95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10)

            for scale in scale_steps:
                if scale < 1.0:
                    resized_width = max(1, int(width * scale))
                    resized_height = max(1, int(height * scale))
                    candidate_image = working_image.resize((resized_width, resized_height), Image.LANCZOS)
                else:
                    candidate_image = working_image

                for quality in quality_steps:
                    candidate_buffer = io.BytesIO()
                    candidate_image.save(
                        candidate_buffer,
                        format='JPEG',
                        optimize=True,
                        progressive=True,
                        quality=quality,
                        subsampling=2,
                    )
                    candidate_content = candidate_buffer.getvalue()
                    if len(candidate_content) <= MAX_UPLOAD_SIZE:
                        return candidate_content

            return None

        if image_format == 'PNG':
            optimized_buffer = io.BytesIO()
            image.save(optimized_buffer, format='PNG', optimize=True, compress_level=9)
            optimized_content = optimized_buffer.getvalue()
            if optimized_content and len(optimized_content) <= MAX_UPLOAD_SIZE:
                optimized_filename = filename.rsplit('.', 1)[0] + '.png'
                return optimized_filename, optimized_content, 'image/png'

            jpeg_content = encode_jpeg_under_limit(image)
            if jpeg_content:
                optimized_filename = filename.rsplit('.', 1)[0] + '.jpg'
                return optimized_filename, jpeg_content, 'image/jpeg'

        elif image_format == 'GIF':
            optimized_buffer = io.BytesIO()
            image.save(optimized_buffer, format='GIF', optimize=True)
            optimized_content = optimized_buffer.getvalue()
            if optimized_content and len(optimized_content) <= MAX_UPLOAD_SIZE:
                optimized_filename = filename.rsplit('.', 1)[0] + '.gif'
                return optimized_filename, optimized_content, 'image/gif'

            jpeg_content = encode_jpeg_under_limit(image)
            if jpeg_content:
                optimized_filename = filename.rsplit('.', 1)[0] + '.jpg'
                return optimized_filename, jpeg_content, 'image/jpeg'

        elif image_format in ('JPEG', 'JPG'):
            lossless_buffer = io.BytesIO()
            image.convert('RGB').save(lossless_buffer, format='JPEG', optimize=True, progressive=True)
            optimized_content = lossless_buffer.getvalue()
            if optimized_content and len(optimized_content) <= MAX_UPLOAD_SIZE:
                optimized_filename = filename.rsplit('.', 1)[0] + '.jpg'
                return optimized_filename, optimized_content, 'image/jpeg'

            jpeg_content = encode_jpeg_under_limit(image)
            if jpeg_content:
                optimized_filename = filename.rsplit('.', 1)[0] + '.jpg'
                return optimized_filename, jpeg_content, 'image/jpeg'

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