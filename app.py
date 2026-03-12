import streamlit as st
import pandas as pd
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


# --------------------
# 入力
# --------------------

st.subheader("データ入力")

type_input = st.selectbox("種類",["収入","支出"])

date = st.date_input("日付")

# カテゴリ候補
income_categories = ["給料","ボーナス","副業","その他"]
expense_categories = ["食費","家賃","光熱費","通信費","交際費","奨学金返済","その他"]

if type_input == "収入":
    category = st.selectbox("カテゴリ", income_categories)
else:
    category = st.selectbox("カテゴリ", expense_categories)

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


# --------------------
# データ表示
# --------------------

data = st.session_state.data

st.subheader("家計簿データ")
st.write(data)


# --------------------
# 削除
# --------------------

if st.button("最後のデータを削除"):
    if len(st.session_state.data) > 0:
        st.session_state.data = st.session_state.data.iloc[:-1]
        st.session_state.data.to_csv("kakeibo.csv", index=False)
        st.rerun()


# --------------------
# 収入支出
# --------------------

income = data[data["type"]=="収入"]["amount"].sum()
expense = data[data["type"]=="支出"]["amount"].sum()

st.subheader("家計状況")

st.write("収入合計:",income)
st.write("支出合計:",expense)

# 残高（追加）
balance = income-expense
st.write("残高:",balance)

if income > 0:
    saving_rate = (income-expense)/income*100
    st.write("貯蓄率:",f"{saving_rate:.1f}%")


# --------------------
# 今月の収支
# --------------------

st.subheader("今月の収支")

data["date"] = pd.to_datetime(data["date"],errors="coerce")

today = pd.Timestamp.today()

this_month = data[
    (data["date"].dt.year == today.year) &
    (data["date"].dt.month == today.month)
]

income_m = this_month[this_month["type"]=="収入"]["amount"].sum()
expense_m = this_month[this_month["type"]=="支出"]["amount"].sum()

st.write("今月の収入:", income_m)
st.write("今月の支出:", expense_m)
st.write("今月の貯蓄:", income_m-expense_m)


# --------------------
# 支出データ
# --------------------

expense_data = data[data["type"]=="支出"]


# --------------------
# 支出ランキング
# --------------------

st.subheader("支出ランキング")

if len(expense_data) > 0:

    ranking = expense_data.groupby("category")["amount"].sum().sort_values(ascending=False)

    st.write(ranking)


# --------------------
# 円グラフ
# --------------------

st.subheader("支出内訳")

if len(expense_data) > 0:

    cat_sum = expense_data.groupby("category")["amount"].sum()

    fig = px.pie(
        values=cat_sum.values,
        names=cat_sum.index,
        title="支出内訳"
    )

    st.plotly_chart(fig)


# --------------------
# 月別支出
# --------------------

st.subheader("月別支出")

if len(expense_data) > 0:

    expense_data = expense_data.copy()
    expense_data["month"] = expense_data["date"].astype(str).str[:7]

    monthly = expense_data.groupby("month")["amount"].sum()

    st.line_chart(monthly)


# --------------------
# CSVダウンロード
# --------------------

st.subheader("データダウンロード")

csv = data.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="CSVダウンロード",
    data=csv,
    file_name="kakeibo.csv",
    mime="text/csv"
)
