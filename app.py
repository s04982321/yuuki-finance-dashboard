import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

st.title("家計簿アプリ")

# データ読み込み
if "data" not in st.session_state:

    if os.path.exists("kakeibo.csv"):
        st.session_state.data = pd.read_csv("kakeibo.csv")
    else:
        st.session_state.data = pd.DataFrame(
            columns=["date","type","category","amount"]
        )

data = st.session_state.data


# 入力
st.subheader("データ入力")

type_input = st.selectbox("種類",["収入","支出"])
date = st.date_input("日付")
category = st.selectbox(
    "カテゴリ",
    ["食費","交通費","娯楽","日用品","その他"]
)
amount = st.number_input("金額",min_value=0)

if st.button("追加"):

    new = pd.DataFrame(
        [[date,type_input,category,amount]],
        columns=["date","type","category","amount"]
    )

    st.session_state.data = pd.concat(
        [st.session_state.data,new],
        ignore_index=True
    )

    st.session_state.data.to_csv("kakeibo.csv",index=False)


# データ表示
data = st.session_state.data

st.subheader("家計簿データ")
st.write(data)


# 削除
if st.button("最後のデータを削除"):
    if len(st.session_state.data) > 0:
        st.session_state.data = st.session_state.data.iloc[:-1]
        st.session_state.data.to_csv("kakeibo.csv", index=False)
        st.rerun()


# 収入支出
income = data[data["type"]=="収入"]["amount"].sum()
expense = data[data["type"]=="支出"]["amount"].sum()

col1, col2 = st.columns(2)

col1.metric("収入合計", income)
col2.metric("支出合計", expense)

if income > 0:
    saving_rate = (income-expense)/income*100
    st.write("貯蓄率:",f"{saving_rate:.1f}%")
else:
    st.write("貯蓄率: 収入データがありません")


# 支出データ
expense_data = data[data["type"]=="支出"]


# 支出ランキング
st.subheader("支出ランキング")

if len(expense_data) > 0:
    ranking = expense_data.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.write(ranking)


# 平均支出
st.subheader("平均支出")

if len(expense_data) > 0:
    avg = expense_data["amount"].mean()
    st.write("1回あたりの平均支出:",round(avg,1))


# 円グラフ（Plotly版）
st.subheader("支出内訳")

if len(expense_data) > 0:

    cat_sum = expense_data.groupby("category")["amount"].sum()

    fig = px.pie(
        values=cat_sum.values,
        names=cat_sum.index,
        title="支出内訳"
    )

    st.plotly_chart(fig)


# 棒グラフ
st.subheader("カテゴリ別支出")

if len(expense_data) > 0:
    cat_sum = expense_data.groupby("category")["amount"].sum()
    st.bar_chart(cat_sum)


# AIコメント
st.subheader("AI家計アドバイス")

if len(expense_data) > 0:

    cat_sum = expense_data.groupby("category")["amount"].sum()

    top_category = cat_sum.idxmax()

    if expense > 0:
        top_ratio = cat_sum.max()/expense*100

        if top_ratio > 40:
            st.write(
                f"{top_category}が支出の{top_ratio:.1f}%を占めています。支出構造を見直すと貯蓄率が改善する可能性があります。"
            )
        else:
            st.write("支出バランスは比較的安定しています。")

# 月別支出
st.subheader("月別支出")

if len(expense_data) > 0:

    expense_data = expense_data.copy()
    expense_data["month"] = expense_data["date"].astype(str).str[:7]

    monthly = expense_data.groupby("month")["amount"].sum()

    st.line_chart(monthly)


# CSVダウンロード
st.subheader("データダウンロード")

csv = data.to_csv(index=False)

st.download_button(
    label="CSVダウンロード",
    data=csv,
    file_name="kakeibo.csv",
    mime="text/csv"
)




