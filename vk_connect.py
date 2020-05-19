
import vk_api

from PIL import Image
import requests
from io import BytesIO
import time

import os
import sys

import math
import random

from user_data import login, password, app_id

from text_finder import get_list_of_text_coords, transfer_text

from groups_id import rus_groups, en_groups

import time


def two_factor():
    code = input('enter code: ')
    remember_device = True
    return code, remember_device
#-194559948 humor21c
#-194490675 test2

def upload_photo(vk_session, photo_path, group_id=-194559948):
    upload = vk_api.VkUpload(vk_session)

    # Загрузка изображения на сервер
    photo_res = upload.photo_wall(photos = photo_path, user_id=531132898, group_id=group_id)

    # Получение id изображения и владельца
    ph_id = photo_res[0]['id']
    ph_owner_id = photo_res[0]['owner_id']

    return ph_id, ph_owner_id

def post_img(vk_session, ph_id, ph_owner_id, group_id=-194559948, publish_date=time.time()+60):
    vk = vk_session.get_api()

    # Добавление в пост изображения и публикация
    res = vk.wall.post(owner_id=group_id, from_group=1, publish_date=publish_date, attachments=f'photo{ph_owner_id}_{ph_id}')


def get_imgs_from_public(vk_session, group_id, amount=50):
    vk = vk_session.get_api()
    post = vk.wall.get(owner_id=group_id, count=amount)
    items = post["items"]

    photo_urls = []

    try:
        for el in items:
            if el["marked_as_ads"] == 0 and 'is_pinned' not in el:
                if 'attachments' in el:
                    for it in el['attachments'][0]:
                        if 'photo' in el['attachments'][0]:
                            photo_urls.append(el['attachments'][0]['photo']['sizes'][-1]['url'])
                            break
    except Exception:
        print(sys.exc_info())
    
    return photo_urls

def get_two_rand_publics():

    if random.randint(0, 20) < 18:
        return rus_groups[random.randint(0, len(rus_groups)-1)] , rus_groups[random.randint(0, len(rus_groups)-1)]
    else:
        return en_groups[random.randint(0, len(en_groups)-1)], en_groups[random.randint(0, len(en_groups)-1)]


def create_meme(vk_session, time_start=time.time(), period=60*30):
    vk = vk_session.get_api()
    group_first,  group_second = get_two_rand_publics()
    while group_second == group_first:
        group_first,  group_second = get_two_rand_publics()
    
    imgs = get_imgs_from_public(vk_session, group_id=group_first)
    imgs.append(get_imgs_from_public(vk_session, group_id=group_second))
    
    try:
        random.shuffle(imgs)
        first_iter = True

        last_img = Image
        cur_img = Image
        counter = 0

        for el in imgs:
            counter += 1
            if first_iter:
                last_img = el
                cur_img = el
                first_iter = False
            else:
                last_img = cur_img
                cur_img = el
            if counter == 2:

                coords_from=get_list_of_text_coords(last_img, web=True)
                if len(coords_from) == 0:
                    counter = 1
                    continue

                coords_to=get_list_of_text_coords(cur_img, web=True)
                if len(coords_to) == 0:
                    counter = 1
                    continue

                response = requests.get(last_img)
                img_from = Image.open(BytesIO(response.content))

                response = requests.get(cur_img)
                img_to = Image.open(BytesIO(response.content))

                res = transfer_text(img_from=img_from, coords_from=coords_from, img_to=img_to, coords_to=coords_to)
                path_f = f'lapenko_{math.floor(time.time()-1589226560)}.png'
                res.save(path_f,"PNG")
                time_start += period
                #post_img(vk_session, *upload_photo(vk_session, path_f, group_id=-194559948), group_id=-194559948, publish_date=time_start)
                #time.sleep(0.5)
                #os.remove(path_f)

                counter = 0

    except Exception:
        print(sys.exc_info())
        return False, time_start

    return True, time_start

def post_meme(vk_session, time_start=time.time(), period=60*30):
    vk = vk_session.get_api()
    group_first,  group_second = get_two_rand_publics()
    while group_second == group_first:
        group_first,  group_second = get_two_rand_publics()
    
    imgs = get_imgs_from_public(vk_session, group_id=group_first)
    imgs.append(get_imgs_from_public(vk_session, group_id=group_second))
    
    try:
        random.shuffle(imgs)
        first_iter = True

        last_img = Image
        cur_img = Image
        counter = 0

        for el in imgs:
            counter += 1
            if first_iter:
                last_img = el
                cur_img = el
                first_iter = False
            else:
                last_img = cur_img
                cur_img = el
            if counter == 2:

                coords_from=get_list_of_text_coords(last_img, web=True)
                if len(coords_from) == 0:
                    counter = 1
                    continue

                coords_to=get_list_of_text_coords(cur_img, web=True)
                if len(coords_to) == 0:
                    counter = 1
                    continue

                response = requests.get(last_img)
                img_from = Image.open(BytesIO(response.content))

                response = requests.get(cur_img)
                img_to = Image.open(BytesIO(response.content))

                res = transfer_text(img_from=img_from, coords_from=coords_from, img_to=img_to, coords_to=coords_to)
                path_f = f'{math.floor(time.time()-1540289822)}.png'
                res.save(path_f,"PNG")
                time_start += period
                post_img(vk_session, *upload_photo(vk_session, path_f, group_id=-194559948), group_id=-194559948, publish_date=time_start)
                time.sleep(0.5)
                os.remove(path_f)

                counter = 0

    except Exception:
        print(sys.exc_info())
        return False, time_start

    return True, time_start


if __name__ == "__main__":
    #-194490675 test2

    random.seed(time.time())

    vk_session = vk_api.VkApi(login, password, auth_handler=two_factor, app_id=app_id, scope='wall, photos')
    vk_session.auth()
    time_s = time.time()
    while True:
        #cont, time_s = create_meme(vk_session, time_start=time_s)
        cont, time_s = post_meme(vk_session, time_start=time_s)
        if not cont:
            break

