import os
from qreader import QReader
import cv2

qreader = QReader()
synonym_bb = ['beauty bomb', 'beautybombrussia', 'beauty', 'bomb']

def read_qrcode(tg_id):
    try:
        image = cv2.cvtColor(cv2.imread(f'users_check/{tg_id}.jpg'), cv2.COLOR_BGR2RGB)
        decoded_text = qreader.detect_and_decode(image=image)
        if decoded_text and decoded_text[-1]:
            decoded_text = decoded_text[-1].replace('&', '=').split('=')
            os.remove(f'users_check/{tg_id}.jpg')
            return f'{decoded_text[1]}{decoded_text[7]}{decoded_text[9]}'
    except:
        return None
    return None


def bb_post_check(text):
    for elem in synonym_bb:
        if elem in text:
            return False
    return True
