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
    global list_channel_message
    return list_channel_message

def rewrite_id_posts(id_posts: str):
    global list_channel_message
    list_channel_message = list(map(int, id_posts.split()))
    with open('app/utils/posts_id.txt', 'r+') as file:
        file.truncate(0)
        file.write(" ".join(str(x) for x in list_channel_message))
        file.close()

def add_new_id_post(id_post: int):
    global list_channel_message
    if len(list_channel_message) == 5:
        list_channel_message.pop()
    list_channel_message.insert(0, id_post)
    with open('app/utils/posts_id.txt', 'r+') as file:
        file.truncate(0)
        file.write(" ".join(str(x) for x in list_channel_message))
        file.close()

list_rolton_item_check = ['роллтон', 'rolton', 'лапша роллтон', 'лапша роллтон beauty bomb мохито', 'мохито']
list_bb_item_check = ['beautybomb', 'bomb', 'beauty bomb', 'hooliguns', 'romcore', 'romecore', 'doll', 'dollhouse',
                      'hs', 'miss', 'plushy', 'sn']
list_promotion_item_check = []
# list_promotion_item_check = [
#                             "Mashed Foundation",
#                             "Party Starter",
#                             "Salt & Pepper",
#                             "Zamazik",
#                             "Noodlicious",
#                             "Rollton",
#                             "Beauty Recipe",
#                             "Browstick",
#                             "Sriracha Plump",
#                             "Lippie Sause",
#                             "Rollton Glaze",
#                             "Glowing Curry",
#                             "Spicy Chicken",
#                             "Herbal Shrimp",
#                             "Avocado & Sea Salt",
#                             "Rosemary & Black Pepper",
#                             "Pumpkin Spice & Basil",
#                             "Ramen Bath",
#                             "Rollton Vibes",
#                             "Double Noodle",
#                             "Snack Break",
#                             "Ramen Extensions"]



def check_items(items):
    res_sum = 0
    points = 0
    rolton_check = False
    promotion_sum = 0
    count_promotion = 0
    for item in items:
        text = item['name'].lower()
        price = int(item['price'])
        flag = False

        for elem in list_rolton_item_check:
            if elem.lower() in text:
                promotion_sum += price
                count_promotion += 1
                rolton_check = True
                flag = True
                break

        if flag:
            continue

        for elem in list_promotion_item_check:
            if elem.lower() in text:
                promotion_sum += price
                count_promotion += 1
                flag = True
                break

        if flag:
            continue

        for elem in list_bb_item_check:
            if elem.lower() in text:
                res_sum += price
                flag = True
                break

        if flag:
            continue

        for item_split in text.split():
            if item_split in list_rolton_item_check:
                rolton_check = True
                promotion_sum += price
                count_promotion += 1
                break
            if item_split in list_promotion_item_check:
                promotion_sum += price
                count_promotion += 1
                break
            if item_split in list_bb_item_check:
                res_sum += price
                break


    flag = True
    if promotion_sum >= 500000:
        points += 3000
    elif promotion_sum >= 300000:
        points += 1600
    elif promotion_sum >= 150000:
        points += 800
    elif promotion_sum >= 80000:
        points += 500
    elif promotion_sum >= 50000:
        points += 300
    elif promotion_sum >= 30000:
        points += 100
    else:
        res_sum += promotion_sum
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
        return None, None, count_promotion, rolton_check
    if flag:
        res_sum += promotion_sum
    return points, res_sum / 100, count_promotion, rolton_check,


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


review_pattern = [
    # Румяна
    "румяна", "румяна party starter", "румяна party start", "party starter",
    "румяна “party starter”", "румяшки", "румяна пати стартэр", "румяна пати стартер",
    "пати стартер", "пати стартэр", "патистартер", "патистартэр", "partystarter",
    "фиолетовые румяна", "сиреневые румяна", "сияющие румяна", "оранжевые румяна",

    # Хайлайтер
    "хайлайтер", "хайлайтеры", "соль перец", "рассыпчатый хайлайтер", "розовый хайлайтер",
    "salt&peper", "salt pepper", "salt&pepper", "хайлайтер соль перец", "хайлайтер соль и перец",

    # Тинт
    "тинт", "тинты", "тинт соус", "красный тинт", "тинт курица", "тинт корова",
    "тинт липи соус", "tint", "tint lippie souse", "lippie souse", "коричневый тинт",

    # Консилер
    "консилер", "консилер замазик", "замазик", "консилеры", "consealer", "consealer zamazik", "zamazik",

    # Тональный крем
    "тональный крем", "тональный", "тоналка", "тон", "тон пюрешка", "пюрешка",
    "пюре", "тон пюре", "mashed", "mashed foundation", "мэшд", "мэшд фоундейшн",

    # Пудра
    "пудра", "матовая пудра", "фиксирующая пудра", "пудра лапша", "лапшичная пудра",
    "powder", "matte powder", "noodlicious", "пудра noodlicious", "noodlicious powder",
    "матирующая пудра", "нудлишес", "пудра нудлишес",

    # Карандаш для глаз
    "карандаш", "карандаши", "карандаш для глаз", "карандаши для глаз",
    "бьюти рецепт", "карандаши бьюти рецепт", "сияющие карандаши", "цветные карандаши",
    "pencil", "eye pencil", "beauty recipes", "beauty recipe", "beauty recipe pencil",

    # Карандаш для бровей
    "карандаш", "карандаш для бровей", "карандаши палочки", "browstick", "brow stick",
    "карандаш browstick", "карандаш brow stick",

    # Плампер для губ
    "плампер", "пламперы", "плампер для губ", "пламперы для губ", "острый плампер",
    "шрирача пламп", "шрирача", "срирача", "sriracha plump", "sriracha", "блестящий плампер",
    "коричневый плампер", "spicy plump", "plumper", "спайси плампер",

    # Bath bomb
    "bath bomb", "bomb bath", "bath bomb ramen", "bath bomb ramen bath", "ramen bath",
    "бомбочка", "бомбочка для ванны", "бомбочка для ванны рамен", "бомбочка рамен",
    "бомбочка лапша", "бомбочка для ванны лапша", "бомбочка ролтон", "бомбочка для ванны роллтон",
    "бомбочка роллтон", "бомбочка для ванны ролтон", "желтая бомбочка",

    # Соль для ванны
    "salt", "bath salt", "salt bath", "salt spicy pumpkin & basil", "bath salt spicy pumpkin & basil",
    "salt spicy pumpkin", "salt pumpkin & basil", "spicy pumpkin & basil", "salt spicy pumpkin basil",
    "spicy pumpkin basil", "bath salt rosemary & black pepper", "bath salt rosemary black pepper",
    "salt rosemary & black pepper", "bath salt rosemary black pepper", "salt rosemary", "salt black pepper",
    "соль", "соль для ванны", "соль для душа", "соль с тыквой", "соль тыква", "соль с тыковкой",
    "соль с тыквой и базиликом", "соль для ванны тыква", "соль для ванны тыква базилик",
    "соль для ванны базилик", "соль тыква", "соль тыква базилик", "соль базилик", "соль с розмарином",
    "соль для ванны с розмарином и перцем", "соль с розмарином и перцем", "розмарин черный перец",
    "соль с перцем", "соль с черным перцем",

    # Маски для лица
    "маска", "масочка", "маски", "масочки", "маска для лица", "масочка для лица",
    "маска с тыквой", "маска для лица с тыквой", "энзимная маска", "энзимная маска с тыквой",
    "тыквенная маска", "жидкая маска", "глоуинг кари", "гловинг кари", "face mask", "glowing curry",
    "энзимы тыквы", "экстракт томата", "томатная маска", "маска с томатом", "маска с помидором",
    "помидор маска", "тканевая маска", "тканевая масочка", "тканевая маска для лица",
    "тканевая маска для лица с помидором", "rollton glaze", "rolton glaze",

    # Кремы для рук
    "крем", "крем для рук", "кремы", "кремы для рук", "крем с курицей", "крем с курочкой",
    "крем с креветкой", "крем с креветками", "hand cream", "hand cream moisturising",
    "herbal shrimp", "крем herbal shrimp", "sos repair", "крем sos repair", "spicy chicken",
    "крем spicy chicken",

    # Масло/гель для душа
    "shower oil", "shower gel", "avocado oil", "shower oil avocado", "shower oil avocado & sea salt",
    "масло", "масло для душа", "гель для душа", "масло с авокадо", "гель с авокадо",
    "масло с авокадо и морской солью",

    # Палетки
    'Палетка "Rollton"', "палетка rollton", "палетка роллтон", "роллтон", "палетка",
    "палеточка", "цветная палетка", "новая палетка", "яркая палетка",

    'отзыв', 'нравится', 'текстура', 'запах', 'дизайн', 'упаковка',
    'крутой', 'цвет', 'состав', 'рекомендую', 'наносится', 'аромат',
    'красиво', 'сияет', 'пигментированный']

def check_review(text):
    if len(text) < 100:
        return False
    for pattern in review_pattern:
        if pattern in text:
            return True
    return False




