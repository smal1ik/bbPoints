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
            os.remove(f'users_check/{tg_id}.jpg')
            id_check = f'{decoded_text[1]}{decoded_text[7]}{decoded_text[9]}'
            data_check = decoded_text[1::2]
            return id_check, data_check
    except:
        return None, None
    return None, None


synonym_bb = ['t.me/beautybombrussia', 't.me/beautybomb', '@beautybomb', '@beautybombrussia']


def bb_post_check(text: str):
    text = text.lower()
    for elem in synonym_bb:
        if elem in text:
            return False
    return True


def add_new_id_post(id_post: int):
    if len(list_channel_message) == 5:
        list_channel_message.pop()
    list_channel_message.insert(0, id_post)
    with open('app/utils/posts_id.txt', 'r+') as file:
        file.truncate(0)
        file.write(" ".join(str(x) for x in list_channel_message))
        file.close()

list_bb_item_check = ['beautybomb', 'bomb', 'beauty bomb']
def check_items(items):
    res_sum = 0
    for item in items:
        text = item['name'].lower()
        price = int(item['price'])
        for elem in list_bb_item_check:
            if elem in text:
                res_sum += price
                break

    if res_sum >= 500000:
        return 3000
    if res_sum >= 300000:
        return 1500
    if res_sum >= 150000:
        return 500
    if res_sum >= 80000:
        return 300
    if res_sum >= 50000:
        return 200
    if res_sum >= 30000:
        return 100

    return None
