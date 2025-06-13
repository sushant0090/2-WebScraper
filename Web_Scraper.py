import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dash import Dash, dcc, html, Input, Output
import base64
import io

data = pd.read_excel("product_data.xlsx")
data["Price"] = data["Price"].str.replace("₹", "").str.replace(",", "")
data["Price"] = pd.to_numeric(data["Price"], errors='coerce')
data["Rating"] = data["Rating"].replace("No Rating", None)
data["Rating_num"] = pd.to_numeric(data["Rating"], errors="coerce")

def encode_plot(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    encoded = base64.b64encode(buffer.getbuffer()).decode("utf8")
    return f"data:image/png;base64,{encoded}"

app = Dash(__name__)
app.title = "New Product Dashboard"

app.layout = html.Div([
    html.H1("🛒 Dashboard View"),
    dcc.Dropdown(
        id="selector",
        options=[{"label": site, "value": site} for site in data["Website"].unique()],
        multi=True,
        placeholder="Choose Website"
    ),
    html.H3("Count View"),
    html.Img(id="out1"),
    html.H3("Mean Price View"),
    html.Img(id="out2"),
    html.H3("Rating-Price Plot"),
    html.Img(id="out3"),
])

@app.callback(
    [Output("out1", "src"),
     Output("out2", "src"),
     Output("out3", "src")],
    [Input("selector", "value")]
)
def refresh_outputs(selected):
    d = data.copy()
    if selected:
        d = d[d["Website"].isin(selected)]

    g1, a1 = plt.subplots()
    sns.countplot(data=d, x="Website", ax=a1)
    a1.set_title("Count by Website")

    g2, a2 = plt.subplots()
    avg = d.groupby("Website")["Price"].mean().reset_index()
    sns.barplot(data=avg, x="Website", y="Price", ax=a2)
    a2.set_title("Average Price")

    g3, a3 = plt.subplots()
    sns.scatterplot(data=d.dropna(subset=["Rating_num"]), x="Rating_num", y="Price", hue="Website", ax=a3)
    a3.set_title("Rating vs Price")

    return encode_plot(g1), encode_plot(g2), encode_plot(g3)

if __name__ == "__main__":
    app.run_server(debug=True)
