import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
from datetime import datetime

st.title("家計簿アプリ")

# データ読み込み
if "data" not in st.session_state:
    if os.path.exists("kakeibo.csv"):
        st.session_state.data = pd.read_csv("kakeibo.csv")
    else:
        st.session_state.data = pd.DataFrame(columns=["日付","項目","金額","種類"])

data = st.session_state.data

st.header("支出・収入入力")

date = st.date_input("日付")
item = st.text_input("項目")
amount = st.number_input("金額", step=1)
type_ = st.selectbox("種類", ["支出","収入"])

if st.button("追加"):
    new_data = pd.DataFrame([[date,item,amount,type_]],columns=data.columns)
    st.session_state.data = pd.concat([data,new_data],ignore_index=True)
    st.session_state.data.to_csv("kakeibo.csv",index=False)
    st.success("追加しました")

st.header("データ")

st.dataframe(st.session_state.data)

# ===== 今月の収支 =====

st.header("今月の収支")

if not st.session_state.data.empty:

    df = st.session_state.data.copy()
    df["日付"] = pd.to_datetime(df["日付"])

    now = datetime.now()

    this_month = df[
        (df["日付"].dt.year == now.year) &
        (df["日付"].dt.month == now.month)
    ]

    income = this_month[this_month["種類"]=="収入"]["金額"].sum()
    expense = this_month[this_month["種類"]=="支出"]["金額"].sum()

    balance = income - expense

    col1,col2,col3 = st.columns(3)

    col1.metric("収入", f"{income}円")
    col2.metric("支出", f"{expense}円")
    col3.metric("収支", f"{balance}円")

# ===== グラフ =====

st.header("支出グラフ")

expense_df = st.session_state.data[
    st.session_state.data["種類"]=="支出"
]

if not expense_df.empty:

    summary = expense_df.groupby("項目")["金額"].sum().reset_index()

    fig = px.pie(
        summary,
        names="項目",
        values="金額",
        title="支出割合"
    )

    st.plotly_chart(fig)

