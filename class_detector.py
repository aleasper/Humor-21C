from torchvision import models
import torch
import argparse
import os
import sys


from text_finder import get_list_of_text_coords, transfer_text

from groups_id import rus_groups, en_groups

from torchvision import transforms

from PIL import Image
import requests
from io import BytesIO

import time
import math

import random

import vk_api

from classes_dict import img_classes

from vk_connect import get_imgs_from_public, post_img, upload_photo

from user_data import login, password, app_id

def two_factor():
    code = input('enter code: ')
    remember_device = True
    return code, remember_device

def construct_arg_parser():
     # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-re", "--reload", type=str, help="path to input from image")
    return vars(ap.parse_args())

def get_img_classes(img_classes, img_path, nn_model, dic_cl_imgs):
    
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
        mean=[0.485, 0.456, 0.406],                
        std=[0.229, 0.224, 0.225]                  
        )])
    response = requests.get(img_path)
    img = Image.open(BytesIO(response.content))
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    nn_model.eval()
    out = nn_model(batch_t)
    classes = [line for line in img_classes]
    #print(classes)
    # Forth, print the top 5 classes predicted by the model
    _, indices = torch.sort(out, descending=True)
    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100
    #print([(img_classes[classes[idx]], percentage[idx].item()) for idx in indices[0][:5]])
    for k in indices[0][:3]:
        dic_cl_imgs[classes[k]].append(img_path)

    return dic_cl_imgs


if __name__ == '__main__':

    random.seed(time.time())

    img_from = Image
    img_to = Image

    #
    dic_cl_imgs = dict()
    for cl in img_classes:
        dic_cl_imgs[cl] = []
    #

    vk_session = vk_api.VkApi(login, password, auth_handler=two_factor, app_id=app_id, scope='wall, photos')
    vk_session.auth()

    urls = []
    random.shuffle(rus_groups)
    for group_id in rus_groups:
        urls.append(get_imgs_from_public(vk_session, group_id=group_id, amount=5))

    args = construct_arg_parser()
    load = args["reload"]
    if load == 'yes':
        the_model = models.resnet101(pretrained=True)
        torch.save(the_model, os.path.join(os.path.abspath(os.getcwd()), 'model.pth'))
        print('saved')
    else: 
        the_model = torch.load(os.path.join(os.path.abspath(os.getcwd()), 'model.pth'))

    
    for img_path_list in urls:
        for img_path in img_path_list:
            dic_cl_imgs = get_img_classes(img_classes, img_path, the_model, dic_cl_imgs)

    time_start = time.time()
    period = 60*30
    for el in dic_cl_imgs:
        if len(dic_cl_imgs[el]) > 1:
            counter = 0
            img_from = Image
            img_to = Image
            coords_from = []
            coords_to = []
            random.shuffle(dic_cl_imgs[el])
            for url in dic_cl_imgs[el]:
                if counter == 0:
                    response = requests.get(url)
                    img_from = Image.open(BytesIO(response.content))
                    coords_from=get_list_of_text_coords(url, web=True)
                    if len (coords_from) == 0:
                        break
                    counter += 1
                else:
                    response = requests.get(url)
                    img_to = Image.open(BytesIO(response.content))
                    coords_to=get_list_of_text_coords(url, web=True)
                    if len (coords_to) == 0:
                        break
                    res = transfer_text(img_from=img_from, coords_from=coords_from, img_to=img_to, coords_to=coords_to)
                    path_f = f'{math.floor(time.time()-1540289822)}.png'
                    res.save(path_f,"PNG")
                    time_start += period
                    #-194490675 test2
                    post_img(vk_session, *upload_photo(vk_session, path_f, group_id=-194490675), group_id=-194490675, publish_date=time_start)
                    time.sleep(0.5)
                    os.remove(path_f)
                    counter = 0

                


