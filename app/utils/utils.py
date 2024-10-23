import os
from qreader import QReader
import cv2

with open('app/utils/posts_id.txt') as file:
    list_channel_message = [int(elem) for elem in file.readline().split()]
print(list_channel_message)

# qreader = QReader()

# def read_qrcode(tg_id):
#     try:
#         image = cv2.cvtColor(cv2.imread(f'users_check/{tg_id}.jpg'), cv2.COLOR_BGR2RGB)
#         decoded_text = qreader.detect_and_decode(image=image)
#         if decoded_text and decoded_text[-1]:
#             decoded_text = decoded_text[-1].replace('&', '=').split('=')
#             os.remove(f'users_check/{tg_id}.jpg')
#             return f'{decoded_text[1]}{decoded_text[7]}{decoded_text[9]}'
#     except:
#         return None
#     return None

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
