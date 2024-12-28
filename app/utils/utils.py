import os
from qreader import QReader
import cv2

with open('app/utils/posts_id.txt') as file:
    list_channel_message = [int(elem) for elem in file.readline().split()]
print(list_channel_message)

qreader = QReader()


def read_qrcode(tg_id):
    try:
        image = cv2.cvtColor(cv2.imread(f'users_check/{tg_id}.jpg'), cv2.COLOR_BGR2RGB)
        decoded_text = qreader.detect_and_decode(image=image)
        if decoded_text and decoded_text[-1]:
            decoded_text = decoded_text[-1].replace('&', '=').split('=')
            id_check = f'{decoded_text[1]}{decoded_text[7]}{decoded_text[9]}'
            data_check = decoded_text[1::2]
            date = data_check[0]
            data_check[0] = f"{date[0:4]}-{date[4:6]}-{date[6:8]}T{date[9:11]}:{date[11:13]}:00"
            return id_check, data_check
        return None, None
    except Exception as e:
        print(e)
        return None, None
    finally:
        os.remove(f'users_check/{tg_id}.jpg')


synonym_bb = ['t.me/beautybombrussia', 't.me/beautybomb', '@beautybomb', '@beautybombrussia', '#bbcore']


def bb_post_check(text: str):
    text = text.lower()
    for elem in synonym_bb:
        if elem in text:
            return False
    return True

def get_id_posts():
    return list_channel_message

def rewrite_id_posts(id_posts: str):
    global list_channel_message
    list_channel_message = id_posts.split()
    with open('app/utils/posts_id.txt', 'r+') as file:
        file.truncate(0)
        file.write(" ".join(str(x) for x in list_channel_message))
        file.close()

def add_new_id_post(id_post: int):
    if len(list_channel_message) == 5:
        list_channel_message.pop()
    list_channel_message.insert(0, id_post)
    with open('app/utils/posts_id.txt', 'r+') as file:
        file.truncate(0)
        file.write(" ".join(str(x) for x in list_channel_message))
        file.close()

list_bb_item_check = ['beautybomb', 'bomb', 'beauty bomb', 'hooliguns', 'romcore', 'romecore']
list_cb_item_check = ['cyberbomb', 'cream blush', 'killer roomba', 'contourator', 'xaela ter', 'eyepocalypce',
                      'not found', 'doomsday', '1101001', 'toxic waste', 'overloaded', 'skipidarushka',
                      'dirty lick', 'robochic', 'machine oil', 'heavy water', 'chrome nails', 'eye protector',
                      'walkie talkie', 'spy drone', 'furiosa']


def check_items(items):
    res_sum = 0
    cyberbomb_sum = 0
    n_cyberbomb_items = 0
    points = 0
    for item in items:
        flag = False
        text = item['name'].lower()
        price = int(item['price'])

        for item_split in text.split():
            if item_split in list_cb_item_check:
                cyberbomb_sum += price
                n_cyberbomb_items += 1
                flag = True
                break
        if flag: continue

        for elem in list_cb_item_check:
            if elem in text:
                cyberbomb_sum += price
                n_cyberbomb_items += 1
                flag = True
                break
        if flag: continue

        for item_split in text.split():
            if item_split in list_bb_item_check:
                res_sum += price
                flag = True
                break
        if flag: continue

        for elem in list_bb_item_check:
            if elem in text:
                res_sum += price
                break

    flag = True
    if cyberbomb_sum >= 500000:
        points += 4000
    elif cyberbomb_sum >= 300000:
        points += 2000
    elif cyberbomb_sum >= 150000:
        points += 800
    elif cyberbomb_sum >= 80000:
        points += 600
    elif cyberbomb_sum >= 50000:
        points += 400
    elif cyberbomb_sum >= 30000:
        points += 200
    else:
        res_sum += cyberbomb_sum
        flag = False

    if res_sum >= 500000:
        points += 1500
    elif res_sum >= 300000:
        points += 800
    elif res_sum >= 150000:
        points += 400
    elif res_sum >= 80000:
        points += 250
    elif res_sum >= 50000:
        points += 150
    elif res_sum >= 30000:
        points += 50
    if points == 0:
        return None, None, n_cyberbomb_items
    if flag:
        res_sum += cyberbomb_sum
    return points, res_sum / 100, n_cyberbomb_items


retail_names = {
    'магнит': ['магнит', 'magnit'],
    'яблоко': ['яблоко', 'золотое яблоко', 'goldapple'],
    'рив': ['рив гош', 'рив', 'rivegauche'],
    'лэтуаль': ['лэтуаль', 'letu'],
    'ozon': ['ozon', 'озон'],
    'wildberries': ['wildberries', 'вайлдберриз'],
    'купер': ['купер', 'kuper'],
    'мегамеркет': ['мегамеркет', 'megamarket']
}

def get_name_retail(retail_place: str):
    for name, synonyms in retail_names.items():
        for synonym in synonyms:
            if synonym in retail_place.lower():
                return name
    return None

list_filter_link_photo = ['vk', 'pinterest', 'dzen', 'instagram', 't.me', 'pin.it']
def filter_link_photo(link):
    for elem in list_filter_link_photo:
        if elem in link:
            return True
    return False



