import os
import cv2
import shutil
import random
import numpy as np
import matplotlib.pyplot as plt


def select_images(path2imgs):
    """
    Select a radom subset of 25% of the images in the directory

    path2imgs (str): path to the directory containing the images
    return (list): Random subset of image paths
    """
    img_list = [file_name for file_name in os.listdir(path2imgs)]
    n = len(img_list)
    return random.choices(img_list, k=n//4)


def merge_images(img1, img2, thresh=200):
    """
    Merges a generated graph image with some noisy document background image

    img1: Image of generated graph
    img2: Background image
    thresh: Threshold value when to consider a pixel as background in the graph image
    return: Merged image
    """
    h, w = img1.shape[0], img1.shape[1]
    img2 = cv2.resize(img2, (w, h))
    blended_img = np.copy(img1)
    blended_img[blended_img >= thresh] = img2[blended_img >= thresh]

    return blended_img


def augment_background(path2imgs, path2bgs, copy_files=False, display=True):
    """
    Adds background noise and gaussian blurring to the graph image

    path2imgs: Path to the directory containing the graph images
    path2bgs: Path to the directory containing the background images
    copy_files: Whether to save the generated image and annotation or not
    display: Whether to display the resulting image or not
    """
    file_names = select_images(path2imgs)

    for file_name in file_names:

        if (not "aug" in file_name) and (file_name.endswith("png")):
            path2file = os.path.join(path2imgs, file_name)
            background_file = random.choice(os.listdir(path2bgs))
            path2background = os.path.join(path2bgs, background_file)
            img1, img2 = cv2.imread(path2file, cv2.IMREAD_GRAYSCALE), cv2.imread(path2background, cv2.IMREAD_GRAYSCALE)
            noisy_img = merge_images(img1, img2)
            filter_dim = random.choice([(3, 3), (5, 5), (7, 7)])
            noisy_img = cv2.GaussianBlur(noisy_img, filter_dim, 0)

            if display:
                plt.figure(figsize=(20, 20))
                plt.imshow(noisy_img)
                plt.show()

            if copy_files:
                cv2.imwrite(os.path.join(path2imgs, f"{file_name[:-4]}_aug.png"), noisy_img)
                label_path = os.path.join(path2imgs, f"{file_name[:-4]}.txt")
                aug_path = os.path.join(path2imgs, f"{file_name[:-4]}_aug.txt")
                seg_label_path = os.path.join('seg_annots', f"{file_name[:-4]}.json")
                seg_aug_label_path = os.path.join('seg_annots', f"{file_name[:-4]}_aug.json")
                shutil.copy(label_path, aug_path)
                shutil.copy(seg_label_path, seg_aug_label_path)
