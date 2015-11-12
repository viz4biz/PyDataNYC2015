"""
utils file
"""
import os
from enaml.icon import Icon, IconImage
from enaml.image import Image
from constants import ICON_DIR


def get_icon(icon_name=None, default_icon='application-blue.png'):
    """
    get icon
    """
    icon_path = ICON_DIR + '/%s' % (icon_name or default_icon)
    if os.path.exists(icon_path):
        return icon_path


def load_icon(icon_name=None):
    """
    load icon image
    """
    image_file = get_icon(icon_name)
    with open(image_file, 'rb') as f:
            data = f.read()
    img = Image(data=data)
    icg = IconImage(image=img)
    return Icon(images=[icg])
