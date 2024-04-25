# 클로버 ocr api
def get_category_result(image_file = './RecipeBOAZ/input/ex.jpg'):

    import requests
    import uuid
    import time
    import json

    import sys
    import io

    import requests
    import urllib

    api_url = 'https://64rr4snprl.apigw.ntruss.com/custom/v1/25675/206e9557ed1ac009e4e1d40622dab52fb515be7ed966afdfb8f018ae51e582a4/document/receipt'
    secret_key = 'naver ocr api secret key'

    output_file = './RecipeBOAZ/output/output.json'

    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
    ('file', open(image_file,'rb'))
    ]
    headers = {
    'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

    res = json.loads(response.text.encode('utf8'))

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(res, outfile, indent=4, ensure_ascii=False)

    # 구매 내역만 추출
    purchase_items = res['images'][0]['receipt']['result']['subResults'][0]['items'] # subR의 items 부분만 추출
    replace_list = []

    ingre_list = []

    for item in purchase_items:
        item_name = item['name']['text'] # 상품 이름
        item_count = item['count']['text'] # 상품 개수
        item_price = item['price']['price']['text'] # 상품 가격
        ingre_list.append(item_name)



    # 전처리 할 때 필요한 함수
    from difflib import SequenceMatcher

    def similar(a, b):  # 단어 간의 유사도 계산
        return SequenceMatcher(None, a, b).ratio()

    def find_most_similar_category(product_name, category_keywords):  # 재료와 유사도 높은 카테고리 찾기
        max_similarity = 0
        matching_category = None

        for category in category_keywords:
            similarity = similar(product_name, category)
            if similarity > max_similarity:
                max_similarity = similarity
                matching_category = category

        return matching_category

    # 카테고리 값 가져오기 함수
    def get_last_category(item):  # 입력값의 카테고리 가져오기
        category_keys = ['category1', 'category2', 'category3', 'category4', 'category5', 'category6']

        last_category = None

        for key in category_keys:
            if key in item and item[key] != "":
                last_category = item[key]
            elif last_category is not None:
                # 현재 키에 대한 값이 없거나 "" 값이라면, 이전 값 유지.
                break

        return last_category


    # 기타채소류 같이 정확하게 카테고리로 나눠지지 않는 경우 -> 처리가 안 됐네
    '''
    etc_ingre = ['루꼴라','샐러리','파슬리','다슬기','유자','아로니아','냉동과일','패션후르츠','용과','두리안','라임','산수유','라즈베리','믹스베리','백년초','코코넛','리치',
                '망고스틴','무화과','황금향','크랜베리','토마토','파파야','사과','복숭아','모과','오디','포포열매','대봉','샤인머스켓','애플망고','골드키위','블루베리','바질',
                '콜라비','야콘','갓','고수','모닝글로리','치커리','그린빈','컬리플라워','토란','케일','네잎클로버','라디치오','고들빼기','양상추','쑥','청경채','궁채','시금치',
                '당근','차요태','허브','양파','삼채','죽순','버터레터스','고구마','앤다이브','달래','쑥갓','신선초','보리','냉이','유채','호박잎','돗나물','레몬그라스','애플민트',
                '알타리','토끼고기','까투리','염소고기','꿩고기','칠면조','차돌박이','말고기','편육','쥐포','오징어','삼겹살','목살','흰살생선','꿀','황금사과','멸치','가자미',
                '박대','보리굴비','과메기','연어회','굴비','우니','성게알','꼴뚜기','오만둥이','고니','명태알','곤이','개불','해물믹스','우렁','한치','호래기','미더덕','캐비어',
                '보말','고동','해파리','굴','냉채','가리비','명란','올갱이육수','아귀','과메기','백합','소라','견과류','캬라멜소스','치즈소스','살사소스','옥수수전분','감자전분',
                '그린너트','바질페스토']
    '''
    category_list = []

    for query1 in ingre_list:
        query = urllib.parse.quote(query1)

        url = "https://openapi.naver.com/v1/search/shop?query=" + query

        request = urllib.request.Request(url)
        request.add_header('X-Naver-Client-Id', 'naver shopping api id')
        request.add_header('X-Naver-Client-Secret', 'naver shopping api pw')

        response = urllib.request.urlopen(request)
        naver = response.read().decode('utf-8')

        data = json.loads(naver) # json -> dict 변경
        items = data.get('items', []) # 필요한 내용 가져오기

        # 재료의 마지막 카테고리
        for item in items:
            last_category = get_last_category(item)
            if last_category==None:
                pass


        # '/'로 분리한 카테고리 단어들
        category_words = last_category.split("/")  
        if len(category_words) >= 2:
            max_similarity = 0
            best_match = None

            # 카테고리 단어들과 상품명 비교
            for word in category_words: # / 로 split한 카테고리 중 실제 재료명과 유사도가 높은 카테고리로 선택
                similarity = similar(word, query1)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = word

            category_list.append(last_category)

    

        elif (last_category == '기타채소류') | (last_category == '기타과일') | (last_category=='기타해산물')|(last_category=='기타생선')|(last_category=='기타잡곡')|(last_category=='기타견과류')|(last_category=='기타건과류')|(last_category=='기타육류')|(last_category=='기타젓갈'):
            matching_category = find_most_similar_category(query1, ingre_list)
            category_list.append(last_category)

        else:
            category_list.append(last_category)
    
    # 제외할 값
    unwanted_values = ['클렌징비누', '기타냉동/간편조리식품']

    # 제외할 값이 리스트에 있다면 제외하고 나머지 값을 chat에 할당
    chat_values = [value for value in category_list if value not in unwanted_values]
    chat_values_str = [str(value) for value in chat_values]
    chat = ','.join(set(chat_values_str)) #중복되는 카테고리 제거
    return(json.dumps(chat, ensure_ascii= False))
