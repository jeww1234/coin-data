#FinanceDataReader 주식, 지수, 환율, 원자재, 암호화폐 등의 
# 금융 데이터를 쉽게 가져올 수 있도록 도와주는 라이브러리
import FinanceDataReader as fdr
import streamlit as st
import datetime
import pandas as pd
import altair as alt

#sidebar -> 왼쪽에 사이드바를 만들어 사용자가 입력할 요소를 배치
with st.sidebar:
    #date_input 사용자에게 날짜를 선택하도록 하는 입력필드드 datetime.datetime(2024,1,1) : 기본값
    date = st.date_input("조회 시작 날짜", datetime.datetime(2024,1,1))
    end_date = st.date_input("조회 종료 날짜", datetime.datetime.today())
    #text_input 사용자에게 텍스트를 입력하도록 하는 입력필드 value="" : 기본값이 빈 문자열이다
    #placeholder : 입력 필드 안에 흐릿하게 보이는 안내 문구
    code = st.text_input('주식 코드', value='', placeholder='주식 코드를 입력해 주세요')
    name_list = fdr.StockListing('KRX')  # 한국 주식시장 목록 가져오기
    if code:
        name = name_list[name_list['Code'] == code]['Name'].values
        # name_list['Code'] == code → name_list 데이터프레임에서 'Code' 값이 code와 같은 행을 찾음.
        # name_list[name_list['Code'] == code] → 위 조건에 맞는 행만 남김.
        # ['Name'] → 찾은 행에서 'Name' 열만 선택
        # .values → 판다스의 Series 형태가 아니라 NumPy 배열로 변환.

        if len(name) > 0:
            stock_name = name[0]
            print(name[0])
        else:
            stock_name = "알 수 없는 종목"
    
    #markdown 파이선에서 html문법을 제한적으로 사용할 수 있게 해줌
    st.markdown('<h1 style="color: blue;">🔗Finance GitHub</h1>',unsafe_allow_html=True)
    st.markdown("[📂깃허브 링크](https://github.com/FinanceData/FinanceDataReader)", unsafe_allow_html=True)
    
    print(name_list)





if code and date:
    df = fdr.DataReader(code, date, end_date)
    df = df.reset_index(drop=False)
    print(df.columns)
    df['단순이동평균(30일)'] = df['Close'].rolling(window=5).mean()
    data = df[['Close', '단순이동평균(30일)']].sort_index(ascending=True)

    tab1, tab2 = st.tabs(['차트', '데이터'])
    #id_vars : 변환 과정에서 유지할 열 / value_vars : 변환될 열을 지정(None이면 모든 열을 변환)
    #var_name : 새로 생길 열의 이름 / value_name : 값을 담을 새로운 열의 이름
    print(df.columns)
    df_melted = df.melt(id_vars=['Date'], value_vars=['Close', '단순이동평균(30일)'],var_name='지표', value_name='값')
    #alt.Chart : 데이터를 기반으로 alt 차트 생성
    #mark_line : 막대그래프
    #encode : 그래프의 세부 속성을 설정
    chart = alt.Chart(df_melted).mark_line().encode(
        x='Date:T',
        y='값:Q',
        #:N은 범주형 데이터임을 명시 -> 데이터 유형을 명확하게 지정하지 않으면 Altair이 자동으로 추론하기 때문에 오류 발성 가능성 있음
        #alt.Scale : 특정 값에 대해 원하는 색을 직접 지정할 수 있게하는 함수
        #domain과 range의 인덱스가 1:1 매칭
        color=alt.Color('지표:N', scale=alt.Scale(domain=['Close','단순이동평균(30일)'],
                                                range=['blue', 'red']))
    ).interactive()#interactive 그래프와 마우스의 상호작용을 가능하게하는 함수
    

    with tab1:
        st.title(f"📈 {stock_name} ({code}) 주가 그래프")
        st.altair_chart(chart, use_container_width=True)
    with tab2:
        st.title(f"📈 {stock_name} ({code}) 주가 데이터")
        st.dataframe(df.sort_index(ascending=False))
        with st.expander('컬럼 설명'):
            st.markdown('''  
            - open : 시가
            - Hight : 고가
            - Low : 저가
            - Close : 종가
            - Adj Close : 수정종가s
            - Volumn : 거래량
        ''')
    