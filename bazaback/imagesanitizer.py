import os
import logging
import magic
import img2pdf
from io import BytesIO
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PIL import Image

from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def check_if_image_file(f):
    file_type = magic.from_file(f, mime=True)
    if file_type:
        if file_type.split('/')[0] == 'image':
            return True
    return False


def convert_image_to_pdf(f):
    pdf_filepath = settings.MEDIA_ROOT + \
        '/tmp/pdf-%s.pdf' % get_random_string(6)
    with open(pdf_filepath, 'wb') as pdf_file, open(f, 'rb') as image_file:
        pdf_file.write(img2pdf.convert(image_file))
    return pdf_filepath


def convert_pdf_to_image(pdf_filepath, img_size):
    try:
        images = convert_from_path(pdf_filepath, size=img_size[0])
        return images[0]
    except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as e:
        return None


def rebuild_image_and_remove_exif(image_file):
    image = Image.open(image_file)
    data = list(image.getdata())
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(data)
    new_image.save(image_file, 'JPEG', quality=50)


def get_raw_image_name(imagedata_name):
    if imagedata_name:
        path_splitted = imagedata_name.split('/')
        if len(path_splitted) > 1:
            return path_splitted[len(path_splitted) - 1].split('.')[0]
        return path_splitted[0].split('.')[0]
    return ''


def sanitize_image(imagedata):
    raw_image_name = get_raw_image_name(imagedata.name)
    raw_image_file_path = settings.MEDIA_ROOT + '/' + default_storage.save(
        'tmp/%s-img' % get_random_string(6), imagedata)
    is_image_file = check_if_image_file(raw_image_file_path)
    logger.info(raw_image_name)
    logger.info(is_image_file)
    if is_image_file:
        img = Image.open(raw_image_file_path)
        raw_image_size = img.size
        if img.mode == 'RGBA':
            img.load()
            background = Image.new("RGB", raw_image_size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            background.save(raw_image_file_path, 'JPEG', quality=50)
        rebuild_image_and_remove_exif(raw_image_file_path)
        converted_pdf_path = convert_image_to_pdf(raw_image_file_path)
        converted_image_from_pdf = convert_pdf_to_image(
            converted_pdf_path, raw_image_size)
        if converted_image_from_pdf:
            os.remove(converted_pdf_path)
            os.remove(raw_image_file_path)
            img_io = BytesIO()
            converted_image_from_pdf.save(img_io, 'JPEG', quality=50)
            return ContentFile(
                img_io.getvalue(),
                '%s.jpg' % raw_image_name if raw_image_name else get_random_string(24))
            # return rebuild_image_and_remove_exif(converted_image_from_pdf, raw_image_name)
    os.remove(raw_image_file_path)
