#server.py
from flask import Flask, request, jsonify
import sys
import api
#api 함수 가져오기
import pymysql
import pandas as pd
import json
#final_recommenadion 함수 가져오기
import final_recommendation

#정규식을 위함
import re

#이미지 가져올 때 사용
import requests
import shutil
import os
from urllib.parse import urlparse

#이미지 저장 시, 시간 및 날짜를 반영해 저장하고자
import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #한글 깨짐 방지용 코드

#api로 레시피 추천하기와 텍스트로 레시피 추천하기를 할 때, 레시피 본문의 형태를 전처리할 때 쓰는 함수 2개
def process_text(text):
    #첫번째로 나오는 1 삭제
    processed_text = re.sub(r'^1(?=\s)', '', text)

    #공백 사이에 있는 숫자를 띄어쓰기 처리하고 오른쪽 공백 삭제
    matches = re.finditer(r'\s(\d+)(\s|$)', processed_text)
    for match in matches:
        number = match.group(1)

        processed_text = re.sub(rf'(?<=\s){number}(\s|$)', '\n', processed_text, count=1)
    return processed_text.strip()

def split_text(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

#public ip로 해당 route에 dataSend된 데이터가 뜨는지 테스트를 위함
#public ip:port번호/keyboard 이렇게 한 채로 
#챗봇이 어떤 메세지 보내고 싶어하는지 보려면 카카오 챗봇 스킬에 입력
@app.route('/keyboard')
def Keyboard():
    dataSend = {
    "Subject":"OSSP",
    "user":"recipe_boaz"
    }
    return jsonify(dataSend)

@app.route('/message', methods=['POST'])
def Message():
    req = request.get_json()
    content = req['userRequest']['utterance']
    print(content)

    if content == u"안녕":
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "type" : "basicCard",
                            "items": [
                                {
                                    "title" : "",
                                    "description" : "안녕하세요"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    return jsonify(dataSend)

#영수증 인식 후 return된 카테고리 값 중에서 하나 입력되는 경우
@app.route('/for_text', methods = ['GET','POST'])
def go_testdb():
    dataSend = {
           "version": "2.0",
           "template": {
               "outputs": [
                   {
                       "simpleText":{
                           "text":"재료를 쉼표로 구분하여 입력해주세요~\n주신 정보를 최대한 포함하여 맛있는 레시피를 추천해드릴게요!^_^\n첫번째로 입력한 값이 주재료가 되어 레시피가 추천됩니다!\nex) 감자,당근,돼지고기\nex) 사과,당근,수박,참>외,메론"
                           }
                       }
                    ]
               }
           }
    return dataSend


@app.route('/text_testdb', methods = ['GET','POST'])
def Texttestdb():
    req = request.get_json()
    content = req['userRequest']['utterance']
    #print(type(content))
    #print(content)
    rec_result = final_recommendation.main_ingre(content)
    rec_result = json.loads(rec_result)
    processed_title = rec_result['menu']["0"]
    processed_description = rec_result['recipe']["0"]
    processed_img_url = rec_result['menu_img']["0"]
    processed_ing = rec_result['ingredient']["0"]
    dataSend = {
           "version": "2.0",
           "template": {
               "outputs": [
                   {
                       "carousel": {
                           "type" : "basicCard",
                           "items": [
                               {
                                   "title" : processed_title,
                                   "description" : processed_ing,
                                   "thumbnail":{
                                       "imageUrl":processed_img_url
                                       }
                                   }
                               ]
                           }
                       }
                   ]
               }
           }
    processed_description = process_text(processed_description)

    processed_description_chunks = split_text(processed_description)
    for i, text_chunk in enumerate(processed_description_chunks):
        dataSend["template"]["outputs"].append({
            "simpleText": {
                "text": f"{text_chunk}"
            },
        })
    print(json.dumps(dataSend, ensure_ascii=False))
    return json.dumps(dataSend, ensure_ascii= False)

@app.route('/api', methods=['GET', 'POST'])
def Api():
    req = request.get_json()
    content = req['action']['detailParams']['secureimage']['origin']
    image_url = re.search(r'List\((.*?)\)', content).group(1)

    image_result = requests.get(image_url, stream = True)

    url_path = urlparse(image_url).path
    image_filename = os.path.basename(datetime.datetime.now().strftime("%Y-%m-%d_%H%M")+'.jpg')

    if image_result.status_code == 200:
        with open('./static/' + image_filename,'wb') as f:
            shutil.copyfileobj(image_result.raw, f)
    image_result.close()

    api_result = api.get_category_result('./static/'+image_filename)
    rec_result = final_recommendation.main_ingre(api_result)
    rec_result = json.loads(rec_result)
    
    processed_title = rec_result['menu']["0"]
    
    processed_description = rec_result['recipe']["0"]

    processed_img_url = rec_result['menu_img']["0"]

    processed_ing = rec_result['ingredient']["0"]

    dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "type" : "basicCard",
                            "items": [
                                {
                                    "title" : processed_title,
                                    "description" : processed_ing,
                                    "thumbnail":{
                                        "imageUrl":processed_img_url
                                        }
                                }
                            ]
                        }

                    }
                ]
            }
        }
    
    processed_description = process_text(processed_description)
    processed_description_chunks = split_text(processed_description)
    for i, text_chunk in enumerate(processed_description_chunks):
        dataSend["template"]["outputs"].append({
            "simpleText": {
                "text": f"{text_chunk}"
            },
        })

    return json.dumps(dataSend, ensure_ascii=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000, debug=True) # Flask 기본포트 5000번