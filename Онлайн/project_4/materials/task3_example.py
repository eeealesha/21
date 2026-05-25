# Пример оформления Задания 3
#
# Это шаблон — он показывает только ФОРМАТ минимального Dash-приложения.
# Конкретные задания и условия — в readme.md.
# Не копируй — пиши свой код самостоятельно!

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# ── Загрузка данных ───────────────────────────────────────────────────────
df = pd.read_csv("../datasets/clinic_visits.csv")   # замени путь если нужно

# ── Приложение ────────────────────────────────────────────────────────────
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Заголовок приложения"),                # замени на нужный

    dcc.Dropdown(
        id="example-dropdown",
        options=[
            {"label": val, "value": val}
            for val in df["specialty"].unique()      # замени столбец
        ],
        value=df["specialty"].iloc[0],               # значение по умолчанию
        clearable=False,
    ),

    dcc.Graph(id="example-chart"),

])

# ── Callback ──────────────────────────────────────────────────────────────
@app.callback(
    Output("example-chart", "figure"),
    Input("example-dropdown", "value"),
)
def update_chart(selected_value):
    filtered = df[df["specialty"] == selected_value]    # замени логику фильтрации

    fig = px.bar(
        filtered,
        x="visit_date",          # замени столбцы на нужные
        y="revenue",
        title=f"График для: {selected_value}",          # замени заголовок
        labels={"visit_date": "Дата", "revenue": "Выручка, ₽"},
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
