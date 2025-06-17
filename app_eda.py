# population_eda_app.py (기존 app_eda.py 기반 수정)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="Population EDA App", layout="wide")

st.title("📊 인구 통계 분석 (Population Trends)")

uploaded_file = st.file_uploader("population_trends.csv 파일 업로드", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 전처리
    df = df.copy()
    df.replace('-', 0, inplace=True)
    df[['인구', '출생아수(명)', '사망자수(명)']] = df[['인구', '출생아수(명)', '사망자수(명)']].apply(pd.to_numeric)

    st.success("✅ 데이터 업로드 및 전처리 완료")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "기초 통계", "연도별 추이", "지역별 분석", "변화량 분석", "시각화"])

    with tab1:
        st.header("1. 기초 통계")
        buffer = io.StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())
        st.dataframe(df.describe())

    with tab2:
        st.header("2. 연도별 인구 추이 (전국)")
        national = df[df['지역'] == '전국']
        fig, ax = plt.subplots()
        sns.lineplot(data=national, x='연도', y='인구', marker='o', ax=ax)

        # 예측
        recent = national[national['연도'] >= national['연도'].max() - 2]
        delta = (recent['출생아수(명)'] - recent['사망자수(명)']).mean()
        future_year = 2035
        last_pop = national['인구'].iloc[-1]
        future_pop = last_pop + (future_year - national['연도'].max()) * delta

        ax.axhline(future_pop, linestyle='--', color='red')
        ax.text(future_year, future_pop, f'Prediction {int(future_pop):,}', color='red')
        st.pyplot(fig)

    with tab3:
        st.header("3. 지역별 인구 변화량 (최근 5년)")
        df_filtered = df[df['지역'] != '전국']
        latest_year = df['연도'].max()
        past_year = latest_year - 5
        latest = df_filtered[df_filtered['연도'] == latest_year]
        past = df_filtered[df_filtered['연도'] == past_year]

        delta_df = latest[['지역', '인구']].merge(past[['지역', '인구']], on='지역', suffixes=('_new', '_old'))
        delta_df['diff'] = delta_df['인구_new'] - delta_df['인구_old']
        delta_df['rate'] = (delta_df['diff'] / delta_df['인구_old']) * 100

        delta_df.sort_values(by='diff', ascending=False, inplace=True)
        fig1, ax1 = plt.subplots()
        sns.barplot(data=delta_df, y='지역', x='diff', ax=ax1)
        ax1.set_title("Population Change (Last 5 Years)")
        st.pyplot(fig1)

        delta_df.sort_values(by='rate', ascending=False, inplace=True)
        fig2, ax2 = plt.subplots()
        sns.barplot(data=delta_df, y='지역', x='rate', ax=ax2)
        ax2.set_title("Population Change Rate (%)")
        st.pyplot(fig2)

    with tab4:
        st.header("4. 인구 증감 상위 100 사례")
        df_non_nat = df[df['지역'] != '전국'].copy()
        df_non_nat['증감'] = df_non_nat.groupby('지역')['인구'].diff()
        top100 = df_non_nat.nlargest(100, '증감')

        def highlight(val):
            color = 'background-color: lightblue' if val > 0 else 'background-color: salmon'
            return color

        st.dataframe(
            top100.style.format({'인구': '{:,}', '증감': '{:,.0f}'})
            .applymap(highlight, subset=['증감'])
        )

    with tab5:
        st.header("5. 시각화 - 누적 영역 그래프")
        pivot = df[df['지역'] != '전국'].pivot(index='연도', columns='지역', values='인구')
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot.plot.area(ax=ax, cmap='tab20')
        ax.set_title("Population by Region (Area Chart)")
        st.pyplot(fig)
else:
    st.info("CSV 파일을 업로드해주세요.")
