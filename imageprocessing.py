import numpy as np
import cv2
import requests
from PIL import Image
from io import BytesIO


def get_img(url, converting = False, save = False):
    print('Geting image by url...', url)
    response = requests.get(url)
    print(response.status_code)
    img = Image.open(BytesIO(response.content))
    if converting:
        img = np.array(img)
    if save:
        img.save(url[-9:])
    return img

def get_gif(url):
    print('Geting animation by url...', url)
    cap = cv2.VideoCapture(url)
    frames = []
    while True:
        ret, frame = cap.read()
        if ret: frames.append(frame)
        else: break
    frames = [Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)) for frame in frames]
    return frames

#image processing

def get_coords(add_url):
    """

    :param add: numpy array
    :param user_pic:
    :return: coords list len 4
    """

    add = get_img(add_url, converting=True)

    hsv_max = np.array((100, 255, 255), np.uint8) #max yellow
    hsv_min = np.array((50, 36, 50), np.uint8) #min yellow


    hsv = cv2.cvtColor(add, cv2.COLOR_BGR2HSV)  # BGR to HSV
    thresh = cv2.inRange(hsv, hsv_min, hsv_max)  # filter color
    contours0, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    coords = None
    for cnt in contours0:
        rect = cv2.minAreaRect(cnt)  # пытаемся вписать прямоугольник
        box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника
        box = np.int0(box)  # округление координат
        area = int(rect[1][0] * rect[1][1])  # вычисление площади
        if area > max_area:
            max_area = area
            coords = box

    a = np.amax(coords.T[0], axis=0) - np.amin(coords.T[0], axis=0) #width of mask
    b = np.amax(coords.T[1], axis=0) - np.amin(coords.T[1], axis=0) #height of mask

    point = (np.amin(coords.T[0], axis=0), np.amin(coords.T[1], axis=0)) #first corner of window

    return (a,b), point

def set_pic(pic, add_url, window_size,  window_point):
    """

    :param pic: PIL.JpegImagePlugin.JpegImageFile
    :param add: numpy array
    :param coords: list len 4
    :return: None
    """

    add = get_img(add_url, converting=True)

    pic = pic.resize(window_size)
    add = Image.fromarray(add.astype('uint8'), 'RGB') #convert to pillow image
    add.paste(pic, box = window_point)

    return add

def set_frames(frames, add_url, window_size,  window_point):
    """

    :param pic: PIL.JpegImagePlugin.JpegImageFile
    :param add: numpy array
    :param coords: list len 4
    :return: None
    """

    add = get_img(add_url, converting=True)
    add_frames = []
    print('start processing frames...')
    for frame in frames:
        frame = frame.resize(window_size)
        add_frame = Image.fromarray(add.astype('uint8'), 'RGB') #convert to pillow image
        add_frame.paste(frame, box = window_point)
        add_frames.append(add_frame)
    return add_frames

def convert_to_bio(pic):
    bio = BytesIO()
    bio.name = 'image.jpeg'
    pic.save(bio, 'JPEG')
    bio.seek(0)
    return bio

def conver_gif_to_bio(frames):
    width, height = frames[0].size
    frames=[frame.resize((300, int(height*300/width))) for frame in frames]
    print(len(frames))
    bio = BytesIO()
    bio.name = 'image.gif'
    frames[0].save(bio,format='GIF',
               save_all=True,
               append_images=frames[1:],      # Pillow >= 3.4.0
               delay=1,
               loop=0)
    bio.seek(0)
    return bio

