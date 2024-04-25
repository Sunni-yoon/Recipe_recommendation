import pymysql
import pandas as pd
import json

def main_ingre(chat = '돼지고기,감자,양파,당근'):  # 주재료 입력받는 함수
    main = chat.split(', ')[0]
    main = main.split(',')
    main_set = set(main)
    main_ox = []

    db = pymysql.connect(host='studydb.chya6eqjrf9f.ap-northeast-2.rds.amazonaws.com', user='boazrcp', password='rcp0914', charset='utf8',db='boaz', port=3306)
    result_df = pd.DataFrame()

    for keyword in main:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM recipetotal WHERE ingredient LIKE %s"
            cursor.execute(sql, ('%' + keyword + '%',))
            results = cursor.fetchall() #list type

            # 결과를 데이터프레임에 추가
            result_df = pd.concat([result_df, pd.DataFrame(results)])
    # intersection 하기 위해서 ingredient 열만 추출
    ingre = result_df[['ingredient']]

    # 각 레시피의 재료들을 모아서 이중리스트로
    ing = []
    for i in range(len(ingre)):
        row_i = ingre.iloc[i].tolist()
        ing.append(row_i)

    ing = [item[0].split(' ') for item in ing]

    # 주재료가 포함된 레시피 main_ox에 1로 표시 후 column 생성
    for menu in ing:
        set_main = set(menu)
        mainox = len(main_set.intersection(set_main))
        main_ox.append(mainox)

    # recipe에 main_ox 컬럼 추가
    result_df['main_ox'] = pd.DataFrame(main_ox)

    # main_ox 가 1인 레시피만 추출
    result_df = result_df[result_df['main_ox']==1]
    # 입력값을 split해서 set1으로!
    chat = chat.split(',')
    set1 = set(chat)
    inter = []


    # 레시피의 인덱스 추출
    recipe_index = result_df.index.to_list()

    # 각 레시피의 재료를 set2으로 만들어서 set1과 set2에 모두 들어있는 재료의 개수를 inter에 append
    for i in recipe_index:
        menu = ing[i]
        set2 = set(menu)
        intersection_count = len(set1.intersection(set2))
        inter.append(intersection_count)

    # recipe에 intersection 컬럼 추가
    df = pd.DataFrame(inter, columns=['intersection'])
    df.set_index(pd.Index(recipe_index), inplace=True)
    result_df = pd.concat([result_df, df], axis=1)

    # intersection이 큰 값부터 10개 추출 후, intersection이 똑같으면 조회수가 높은 순서대로 정렬
    idx = result_df['intersection'].nlargest(10).index
    rec = result_df.loc[idx, :].sort_values(by=['intersection', 'view'], ascending=[False, False]).reset_index()
    rec = result_df.sort_values(by=['intersection', 'view'], ascending=[False, False]).reset_index()

    # rec['intersection']이 0 인 행의 인덱스
    # (start_zero[0]이 1이면 -> 그 재료에 해당하는 레시피 없음)
    start_zero = [i for i, value in enumerate(rec['intersection']) if value == 0.0]

    # 레시피 추천
    # 1. rec에 intersection이 0인 값이 없으면 그냥 순서대로 추천
    if not start_zero:
        recs = rec.iloc[:3, [1, 2, 3, 4, 5, 6, 8]]
        return json.dumps(recs.to_dict(), ensure_ascii= False)
    elif start_zero[0] > 3: # intersection이 3초과이면 일단 3개만 추천하고 stop!
        recs = rec.iloc[:3, [1, 2, 3, 4, 5, 6, 8]]
        return json.dumps(recs.to_dict(), ensure_ascii= False)

    elif start_zero[0] <= 3: # intersection이 3이하이면 일단 0이 아닌 레시피만 >추천하고 stop!
        recs = rec.iloc[:3, [1, 2, 3, 4, 5, 6, 8]]
        return json.dumps(recs.to_dict(), ensure_ascii= False)
    else:
        print('추천할 레시피가 없습니다. 재료를 더 입력해주세요')

    #로컬에서 적용하려고 했던 코드
    '''
    # 1. rec에 intersection이 0인 값이 없으면 그냥 순서대로 추천
    if not start_zero:
        recs = [rec.iloc[i, [1, 2, 3, 4, 5, 6]].values.tolist() for i in range(3)]
        for rec_i in recs:  # 3개 먼저 추천 후
            print(rec_i)
            return_df = return_df.append(pd.DataFrame([rec_i], columns = ['menu','member','minute','level','ingredient','recipe']), ignore_index = True)

        for i in range(3, 10):  # 다른 레시피가 필요하다고 하면 하나씩 더 추천
            answer = input('다른 레시피가 더 필요하신가요? (yes/no): ')
            if answer.lower() != 'yes':
                break
            else:
                rec_i = rec.iloc[i, [1, 2, 3, 4, 5, 6]].values.tolist()
                print(rec_i)
                return_df = return_df.append(pd.DataFrame([rec_i], columns = ['menu','member','minute','level','ingredient','recipe']), ignore_index = True)
            
    # 2. rec에 intersection이 0인 값이 있으면 0이 나오기 전까지만 추천하고 '더 이상 추천할 레시피가 없습니다.'' 출력
    elif start_zero[0] > 3: # intersection이 3초과이면 일단 3개만 추천하고 stop!
        recs = [rec.iloc[0:3, [1, 2, 3, 4, 5, 6]].values.tolist() for i in range(3)]
        for rec_i in recs:
            print(rec_i)
            return_df = return_df.append(pd.DataFrame([rec_i], columns = ['menu','member','minute','level','ingredient','recipe']), ignore_index = True)

            answer = input('다른 레시피가 더 필요하신가요? (yes/no): ')
            if answer.lower() != 'yes':
                break
            else:
                print('더 이상 추천할 레시피가 없습니다.')
                break
            
            
                
    elif start_zero[0] <= 3: # intersection이 3이하이면 일단 0이 아닌 레시피만 추천하고 stop!
        recs = [rec.iloc[start_zero[0], [1, 2, 3, 4, 5, 6]].values.tolist() for i in range(3)]
        for rec_i in recs:
            print(rec_i)
            return_df = return_df.append(pd.DataFrame([rec_i], columns = ['menu','member','minute','level','ingredient','recipe']), ignore_index = True)
            answer = input('다른 레시피가 더 필요하신가요? (yes/no): ')
            if answer.lower() != 'yes':
                print('더 이상 추천할 레시피가 없습니다.')
                break    
                
    # 3. intersection이 전부 0이면 print('추천할 레시피가 없습니다. 재료를 더 입력해주세요')
    else: 
        print('추천할 레시피가 없습니다. 재료를 더 입력해주세요')
    '''

    import pymysql
    import pandas as pd

    db =pymysql.connect(host='db주소', user='dbid', password='dbpw', charset='utf8',db='dbdb', port=3306)
    result_df = pd.DataFrame()

    main = '김'
    main = main.split(',')
    main_set = set(main)
    main_ox = []

    for keyword in main:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM dbtable WHERE ingredient LIKE %s" 
            cursor.execute(sql, ('%' + keyword + '%',))
            results = cursor.fetchall() #list type

            # 결과를 데이터프레임에 추가
            result_df = pd.concat([result_df, pd.DataFrame(results)])

    # intersection 하기 위해서 ingredient 열만 추출
    ingre = result_df[['cleaned_ingredient']]

    # 각 레시피의 재료들을 모아서 이중리스트로
    ing = []
    for i in range(len(ingre)):
        row_i = ingre.iloc[i].tolist()
        ing.append(row_i)

    ing = [item[0].split(' ') for item in ing] 



    # 입력값을 split해서 set1으로!

    chat = '김,밥공기,나또팩,겨자소스'
    chat = chat.split(',')
    set1 = set(chat)
    inter = []


    # 주재료가 포함된 레시피 main_ox에 1로 표시 후 column 생성
    for menu in ing:
        set_main = set(menu)
        mainox = len(main_set.intersection(set_main))
        main_ox.append(mainox)


    # recipe에 main_ox 컬럼 추가
    result_df['main_ox'] = pd.DataFrame(main_ox)

    # main_ox 가 1인 레시피만 추출
    result_df = result_df[result_df['main_ox']==1]

    # 레시피의 인덱스 추출
    recipe_index = result_df.index.to_list()

    # 각 레시피의 재료를 set2으로 만들어서 set1과 set2에 모두 들어있는 재료의 개수를 inter에 append
    for i in recipe_index:
        menu = ing[i]
        set2 = set(menu)
        intersection_count = len(set1.intersection(set2))
        inter.append(intersection_count)

    # recipe에 intersection 컬럼 추가
    df = pd.DataFrame(inter, columns=['intersection'])
    df.set_index(pd.Index(recipe_index), inplace=True)
    result_df = pd.concat([result_df, df], axis=1)

    # intersection이 큰 값부터 10개 추출 후, intersection이 똑같으면 조회수가 높은 순서대로 정렬
    idx = result_df['intersection'].nlargest(10).index
    rec = result_df.loc[idx, :].sort_values(by=['intersection', 'view'], ascending=[False, False]).reset_index()
    rec = result_df.sort_values(by=['intersection', 'view'], ascending=[False, False]).reset_index()

    # rec['intersection']이 0 인 행의 인덱스
    # (start_zero[0]이 1이면 -> 그 재료에 해당하는 레시피 없음)
    start_zero = [i for i, value in enumerate(rec['intersection']) if value == 0.0]


    # 레시피 추천
    # 1. rec에 intersection이 0인 값이 없으면 그냥 순서대로 추천
    if not start_zero:
        recs = [rec.iloc[i, [1, 2, 3, 4, 5, 6]].values.tolist() for i in range(3)]
        for rec_i in recs:  # 3개 먼저 추천 후
            print(rec_i)
        for i in range(3, 10):  # 다른 레시피가 필요하다고 하면 하나씩 더 추천
            answer = input('다른 레시피가 더 필요하신가요? (yes/no): ')
            if answer.lower() != 'yes':
                break
            else:
                rec_i = rec.iloc[i, [1, 2, 3, 4, 5, 6]].values.tolist()
                print(rec_i)
            
    # 2. rec에 intersection이 0인 값이 있으면 0이 나오기 전까지만 추천하고 '더 이상 추천할 레시피가 없습니다.'' 출력
    elif start_zero[0] > 3: # intersection이 3초과이면 일단 3개만 추천하고 stop!
        recs = [rec.iloc[0:3, [1, 2, 3, 4, 5, 6]].values.tolist() for i in range(3)]
        for rec_i in recs:
            print(rec_i)
            answer = input('다른 레시피가 더 필요하신가요? (yes/no): ')
            if answer.lower() != 'yes':
                break
            else:
                print('더 이상 추천할 레시피가 없습니다.')
                break
            
            
                
    elif start_zero[0] <= 3: # intersection이 3이하이면 일단 0이 아닌 레시피만 추천하고 stop!
        recs = [rec.iloc[start_zero[0], [1, 2, 3, 4, 5, 6]].values.tolist() for i in range(3)]
        for rec_i in recs:
            print(rec_i)
            answer = input('다른 레시피가 더 필요하신가요? (yes/no): ')
            if answer.lower() != 'yes':
                print('더 이상 추천할 레시피가 없습니다.')
                break    
                
    # 3. intersection이 전부 0이면 print('추천할 레시피가 없습니다. 재료를 더 입력해주세요')
    else: 
        print('추천할 레시피가 없습니다. 재료를 더 입력해주세요')