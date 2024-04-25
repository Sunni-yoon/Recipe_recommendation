# Recipe_recommendation

## Notice
- 입력받은 음식 재료를 기반으로 레시피를 추천해주는 레시피 추천 챗봇 구현
  
```api.py``` : CLOVA api 및 네이버 api 불러오기 <br/>
```server.py``` : 서버 구축 <br/>
```final_recommendation.py``` : 추천 기능 구현 <br/>

----------------------------------------------------------------------

## 프로젝트 내용 </br>

- 카카오톡 챗봇으로 사용자에게 재료를 입력받아 레시피를 추천해주는 기능 구현
1.  영수증 이미지 OCR을 통한 추천
2.  사용자에게 직접 텍스트를 입력받아 추천

<br/>

![image](https://github.com/Sunni-yoon/Recipe_recommendation/assets/118954283/39c6caeb-8477-4e25-93b4-6879df5d1c36)


![image](https://github.com/Sunni-yoon/Recipe_recommendation/assets/118954283/dfdbcf24-bd6e-481e-88b9-0eeb16fbedde)

- CLOVA OCR API를 사용하여 영수증 내의 재료를 인식

![image](https://github.com/Sunni-yoon/Recipe_recommendation/assets/118954283/e559d6e0-1b8d-4c7d-bf48-26600154928b)

- OCR을 통해 인식된 재료/직접 입력받은 재료 -> 네이버 쇼핑 검색 API를 사용하여 재료명 전처리

  ![image](https://github.com/Sunni-yoon/Recipe_recommendation/assets/118954283/2b0a7c99-9de7-41f3-8d84-7078d2977754)

- 포함된 재료를 바탕으로 레시피 DB에서 데이터 불러오기

![image](https://github.com/Sunni-yoon/Recipe_recommendation/assets/118954283/c7d0aa94-a1a5-45b4-a159-1475e757a21e)

- 재료 교집합을 통해 가장 재료가 많이 들어간 순서대로 레시피 추천

  ![image](https://github.com/Sunni-yoon/Recipe_recommendation/assets/118954283/af0d5a18-3537-4fa9-9ca3-97de44bb0abf)

- 실제 챗봇 구현을 통해 추천
<br/>

더 자세한 내용은 **레시피를보아즈_발표자료** 를 참고해주세요.
