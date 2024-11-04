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


def get_items_from_result(result):
    result = result['soap:Envelope']['soap:Body']['GetMessageResponse']['Message']['GetTicketResponse'][
        'Result']['Ticket']
    result = json.loads(result)
    items = result['content']['items']
    res_items = []
    for item in items:
        res_items.append({'name': item['name'], 'price': item['price']})
    return res_items


def exec_request(req, body, headers, n, slp):
    for _ in range(n):
        r = requests.post(req, data=body, headers=headers)
        result = xmltodict.parse(r.text)
        status = result['soap:Envelope']['soap:Body']['GetMessageResponse']['ProcessingStatus']
        if status == 'COMPLETED':
            return get_items_from_result(result)
        time.sleep(slp)
    return None


def get_items_check(sum, date, fn, fiscal_document_id, fiscal_sign):
    token = auth()
    check_id = send_message_request(token, sum, date, fn, fiscal_document_id, fiscal_sign)
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