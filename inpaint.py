import cv2
from simple_lama_inpainting import SimpleLama
from PIL import Image
import numpy as np

from utils import load_image, opencv_display_image, dilate_image, save_image


def inpaint_image(img_path, mask_path, result_path):
    """

    :param img_path: original image path (probably png)
    :param mask_path: mask image path (probably png)
    :param result_path: result image path (probably png)
    :return:
    """
    # image = Image.open(img_path)
    # mask = Image.open(mask_path).convert('L')
    image = load_image(img_path)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mask = load_image(mask_path)
    mask_grey = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask_grey = dilate_image(mask_grey, mask=(15, 15), iterations=4)
    image_masked = cv2.bitwise_and(image, image, mask=(255 - mask_grey))
    simple_lama = SimpleLama()
    healed_image = simple_lama(image_masked, mask_grey)
    healed_image_np = np.array(healed_image)
    # healed_image = cv2.cvtColor(healed_image_np, cv2.COLOR_RGB2BGR)

    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # image_masked = cv2.cvtColor(image_masked, cv2.COLOR_RGB2BGR)
    images_grid = cv2.vconcat([
        cv2.hconcat([image, image_masked, ]),
        cv2.hconcat([healed_image_np, healed_image_np - image_masked])])

    opencv_display_image(images_grid, 'Source and Target')
    # healed_image_np = cv2.cvtColor(healed_image_np, cv2.COLOR_BGR2RGB)
    opencv_display_image(healed_image_np, 'Healed Image RGB')
    save_image(healed_image_np, result_path)
    return healed_image_np


# inpaint_image(img_path, mask_path, result_path)
