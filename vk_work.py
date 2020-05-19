
import vk_api

from PIL import Image
import requests
from io import BytesIO
import time

import os
import sys

import math
import random

from user_data import login, password

from text_finder import get_list_of_text_coords, transfer_text

import time


def upload_photo(vk_session, photo_path):
    upload = vk_api.VkUpload(vk_session)

    # Загрузка изображения на сервер
    photo_res = upload.photo_wall(photos = photo_path, user_id=531132898, group_id=-194490675)

    # Получение id изображения и владельца
    ph_id = photo_res[0]['id']
    ph_owner_id = photo_res[0]['owner_id']

    return ph_id, ph_owner_id

def post_img(vk_session, ph_id, ph_owner_id):
    vk = vk_session.get_api()

    # Добавление в пост изображения и публикация
    res = vk.wall.post(owner_id=-194490675, from_group=1, attachments=f'photo{ph_owner_id}_{ph_id}')


def get_imgs_from_public(vk_session, group_id, amount=30):
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

def get_rand_public():
    '''lapenko''' '''2ch''' '''4ch''' '''trash'''
    '''mdk''' '''orlenok''' '''stolbnyak''' '''igm'''
    '''nenormalno''' '''beobanka''' '''glub po smislu prikoli''' '''dobraya postiron'''
    rus_groups = [-192329801, -34824571, -45745333, -152435896,\
        -57846937, -36775802, -35294456, -30602036,\
            -141959356, -67185996,  -168381351, -184003532]

    '''dank memes''' '''beobanka''' '''eternal classic''' '''reddit'''
    en_groups = [-120254617, -67185996, -129440544, -150550417]

    if random.randint(0, 10) < 8:
        return rus_groups[random.randint(0, len(rus_groups)-1)]
    else:
        return en_groups[random.randint(0, len(en_groups)-1)]


def post_meme(vk_session, rus_groups, en_groups):
    vk = vk_session.get_api()

    group_first = get_rand_public()
    group_second = get_rand_public()
    while group_second == group_first:
        group_second = get_rand_public()

    #post = (vk.wall.get(owner_id=get_rand_public(), count=10))
    imgs = get_imgs_from_public(vk_session, group_id=group_first)
    imgs.append(get_imgs_from_public(vk_session, group_id=group_second))

        last_posts = post
        while post == last_posts:
            post = (vk.wall.get(owner_id=groups_id[random.randint(0, len(groups_id) - 1)], count=10))

        for el in post["items"]:
            if el["marked_as_ads"] == 0 and 'is_pinned' not in el:
                if 'attachments' in el:
                    for it in el['attachments'][0]:
                        if 'photo' in el['attachments'][0]:
                                photo_url.append(el['attachments'][0]['photo']['sizes'][-1]['url'])
                                break
        
        random.shuffle(photo_url)
        first_iter = True

        last_img = Image
        cur_img = Image
        counter = 0

        for el in photo_url:
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
                post_img(vk_session, *upload_photo(vk_session, path_f))
                os.remove(path_f)

                counter = 0

    except Exception:
        print(sys.exc_info())


if __name__ == "__main__":

    random.seed(time.time())

    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    post_meme(vk_session, rus_groups, en_groups)
    

