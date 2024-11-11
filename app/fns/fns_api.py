import json
import time
import requests
import xmltodict

auth_token = "JczBEFRCanxmhiYDkVB0iUKuorPSQmi2NcLFeEmS0N6uy4FFLRdmhxmchtbgIGbBOs3tywuzapevgCwKNoP67Hzw8NVQu0Y9bpgRZkgNDPvXvYyzXoF9Tlp3bh2GhWr6"
headers = {'content-type': 'text/xml;charset=UTF-8'}
url = "https://openapi.nalog.ru:8090/open-api/"


def auth():
    body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="urn://x-artefacts-gnivc-ru/inplat/servin/OpenApiMessageConsumerService/types/1.0">
       <soapenv:Header/>
       <soapenv:Body>
          <ns:GetMessageRequest>
             <ns:Message>
                <tns:AuthRequest xmlns:tns="urn://x-artefacts-gnivc-ru/ais3/kkt/AuthService/types/1.0">
                   <tns:AuthAppInfo>
                   <tns:MasterToken>{auth_token}</tns:MasterToken>
                   </tns:AuthAppInfo>
                </tns:AuthRequest>
             </ns:Message>
          </ns:GetMessageRequest>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    req = url + "AuthService/0.1/1.1"
    r = requests.post(req, data=body, headers=headers)
    result = xmltodict.parse(r.text)
    try:
        return result['soap:Envelope']['soap:Body']['GetMessageResponse']['Message']['AuthResponse']['Result']['Token']
    except:
        return None


def send_message_request(token, sum, date, fn, fiscal_document_id, fiscal_sign):
    headers['FNS-OpenApi-Token'] = token
    body = f"""<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
        <soap-env:Body>
            <ns0:SendMessageRequest xmlns:ns0="urn://x-artefacts-gnivc-ru/inplat/servin/OpenApiAsyncMessageConsumerService/types/1.0">
                <ns0:Message>
                    <tns:GetTicketRequest xmlns:tns="urn://x-artefacts-gnivc-ru/ais3/kkt/KktTicketService/types/1.0">
        <tns:GetTicketInfo>
        <tns:Sum>{sum}</tns:Sum>
            <tns:Date>{date}</tns:Date>
            <tns:Fn>{fn}</tns:Fn>
            <tns:TypeOperation>1</tns:TypeOperation>
            <tns:FiscalDocumentId>{fiscal_document_id}</tns:FiscalDocumentId>
            <tns:FiscalSign>{fiscal_sign}</tns:FiscalSign>
            <tns:RawData>true</tns:RawData>
            </tns:GetTicketInfo>
        </tns:GetTicketRequest>
                </ns0:Message>
            </ns0:SendMessageRequest>
        </soap-env:Body>
    </soap-env:Envelope>
    """
    req = url + "ais3/KktService/0.1/1.1"
    r = requests.post(req, data=body, headers=headers)
    result = xmltodict.parse(r.text)
    try:
        return result['soap:Envelope']['soap:Body']['SendMessageResponse']['MessageId']
    except:
        return None


a = {'id': 3612821491523884288, 'ofdId': 'ofd26', 'receiveDate': '2019-12-15T14:21:51Z', 'subtype': 'receipt',
 'address': '140404, Московская обл, Коломна г, Гаврилова ул, дом № 1,пом.181', 'content': {
    'rawData': 'AwCdAhEEEAA5Mjg1MDAwMTAwMTUwMTc1DQQUADAwMDA1NDg5NjcwMTkzMzggICAg+gMMADIzMTAwMzE0NzUgIBAEBABCkwAA9AMEAEBr9l01BAYAMQQX3W/YDgQEAPIAAAASBAQAIAEAAB4EAQAB/AMDAEwLASMEVgAGBDAAQkVBVVRZIEJPTUIggaul4aogpKvvIKPjoSBCRkYg4jAyKIOgrKygIIqu4ayl4qiqNwQCAExA/wMCAAABEwQCAExArwQBAAGwBAIAtwq+BAEABCMEVgAGBDAAQkVBVVRZIEJPTUIgj6CrpeKqoCDipa2lqSBFeWVzaGFkb3cgQkZGIDAxIChaaGVqNwQCAJhY/wMCAAABEwQCAJhYrwQBAAGwBAIAxA6+BAEABCMEVgAGBDAAQkVBVVRZIEJPTUIglaCpq6Cp4qXgIERpYW1vbmQgQkZGIOIwMShaaGVqaWFuZyk6NwQCAChY/wMCAAABEwQCAChYrwQBAAGwBAIAsQ6+BAEABCMEVgAGBDAAU0tJTkxJVEUgjKDhqqAgrqyuq6CmIK8vo6ugpyDhIKquq6ugoyAzMOjiKJ2koqitNwQCAEAa/wMCAAABEwQCAEAarwQBAAGwBAIAYAS+BAEABAcEAQAAOQQDAEwLAb8EAQAAwAQBAADBBAEAAP0DGQCSrqKg4K6ipaQgrKCjoKeoraAgmKjorqKgHwQBAAEkBAwAd3d3Lm5hbG9nLnJ1owQUAIygo62o4iCKruGspeKoqiCRoOKoGAQLAICOICKSoK2kpeAi8QNAADE0MDQwNCwgjK7hqq6i4aqg7yCuoassIIquq66sraAgoywgg6Ci4KirrqKgIOOrLCCkrqwg/CAxLK+urC4xODG5BAEAAk4EAgCNLIEG+v5N7DFn',
    'messageFiscalSign': 9297394450888929639, 'code': 3, 'fiscalDriveNumber': '9285000100150175',
    'kktRegId': '0000548967019338', 'userInn': '2310031475', 'fiscalDocumentNumber': 37698, 'dateTime': 1576430400,
    'fiscalSign': 400388056, 'shiftNumber': 242, 'requestNumber': 288, 'operationType': 1, 'totalSum': 68428, 'items': [
        {'name': 'BEAUTY BOMB Блеск для губ BFF т02(Гамма Косметик', 'price': 16460, 'quantity': 1.0, 'sum': 16460,
         'nds': 1, 'ndsSum': 2743, 'paymentType': 4},
        {'name': 'BEAUTY BOMB Палетка теней Eyeshadow BFF 01 (Zhej', 'price': 22680, 'quantity': 1.0, 'sum': 22680,
         'nds': 1, 'ndsSum': 3780, 'paymentType': 4},
        {'name': 'BEAUTY BOMB Хайлайтер Diamond BFF т01(Zhejiang):', 'price': 22568, 'quantity': 1.0, 'sum': 22568,
         'nds': 1, 'ndsSum': 3761, 'paymentType': 4},
        {'name': 'SKINLITE Маска омолаж п/глаз с коллаг 30шт(Эдвин', 'price': 6720, 'quantity': 1.0, 'sum': 6720,
         'nds': 1, 'ndsSum': 1120, 'paymentType': 4}], 'cashTotalSum': 0, 'ecashTotalSum': 68428, 'prepaidSum': 0,
    'creditSum': 0, 'provisionSum': 0, 'operator': 'Товаровед магазина Шишова', 'appliedTaxationType': 1,
    'fnsUrl': 'www.nalog.ru', 'retailPlace': 'Магнит Косметик Сати', 'user': 'АО "Тандер"',
    'retailPlaceAddress': '140404, Московская обл, Коломна г, Гаврилова ул, дом № 1,пом.181',
    'fiscalDocumentFormatVer': 2, 'nds18': 11405}}


def get_items_from_result(result):
    result = result['soap:Envelope']['soap:Body']['GetMessageResponse']['Message']['GetTicketResponse'][
        'Result']['Ticket']
    result = json.loads(result)
    items = result['content']['items']
    res_items = []
    print(result['content']['retailPlace'])
    for item in items:
        res_items.append({'name': item['name'], 'price': item['price']})
    return res_items


def exec_request(req, body, headers, n, slp):
    for _ in range(n):
        try:
            r = requests.post(req, data=body, headers=headers)
            result = xmltodict.parse(r.text)
            status = result['soap:Envelope']['soap:Body']['GetMessageResponse']['ProcessingStatus']
            if status == 'COMPLETED':
                return get_items_from_result(result)
            time.sleep(slp)
        except:
            return None
    return None


def get_items_check(data_check):
    s = data_check[1].replace('.', '')
    date = data_check[0]
    fn = data_check[2]
    fiscal_document_id = data_check[3]
    fiscal_sign = data_check[4]
    token = auth()
    if token is None:
        print("token", token)
        return None
    check_id = send_message_request(token, s, date, fn, fiscal_document_id, fiscal_sign)
    if check_id is None:
        print("check_id", check_id)
        return None
    headers['FNS-OpenApi-Token'] = token
    req = url + "ais3/KktService/0.1/1.1"
    body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="urn://x-artefacts-gnivc-ru/inplat/servin/OpenApiAsyncMessageConsumerService/types/1.0">
       <soapenv:Header/>
       <soapenv:Body>
          <ns:GetMessageRequest>
             <ns:MessageId>{check_id}</ns:MessageId>
          </ns:GetMessageRequest>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    timing = [[5, 2], [5, 3], [2, 4]]
    for n, slp in timing:
        res = exec_request(req, body, headers, n, slp)
        if res is not None:
            return res
    return None
