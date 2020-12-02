import os
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


def rebuild_image_and_remove_exif(image, filename):
    data = list(image.getdata())
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(data)
    img_io = BytesIO()
    new_image.save(img_io, 'JPEG', quality=80)
    # TODO: Get original file name
    return ContentFile(
        img_io.getvalue(),
        '%s.jpg' % filename if filename else get_random_string(24))


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
    if is_image_file:
        img = Image.open(raw_image_file_path)
        raw_image_size = img.size
        if img.mode == 'RGBA':
            img.load()
            background = Image.new("RGB", raw_image_size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            background.save(raw_image_file_path, 'JPEG', quality=80)
        converted_pdf_path = convert_image_to_pdf(raw_image_file_path)
        converted_image_from_pdf = convert_pdf_to_image(
            converted_pdf_path, raw_image_size)
        if converted_image_from_pdf:
            os.remove(converted_pdf_path)
            os.remove(raw_image_file_path)
            return rebuild_image_and_remove_exif(converted_image_from_pdf, raw_image_name)
    os.remove(raw_image_file_path)
