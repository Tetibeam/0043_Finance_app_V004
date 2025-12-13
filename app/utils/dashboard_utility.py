import plotly.io as pio
import plotly.graph_objects as go

def make_vector(current, previous):
    if previous == 0:
        return 0
    rate = current / previous
    if rate > 1.005:
        return 1
    elif rate < 0.995:
        return -1
    else:
        return 0

def make_graph_template():
    theme = go.layout.Template(
        layout=go.Layout(
            autosize=True, margin=dict(l=50,r=30,t=10,b=40),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            font=dict(family="Inter, Roboto", size=14, color="#DDDDDD"),

            xaxis=dict(
                title=dict(font_size=12),
                title_standoff=16,
                tickfont=dict(size=10),
                showgrid=True,
                gridcolor="#444444",
                zeroline=False,
                color="#cccccc"
            ),
            
            yaxis=dict(
                title=dict(font_size=12),
                title_standoff=16,
                separatethousands=False,
                tickfont=dict(size=10),
                showgrid=True,
                gridcolor="#444444",
                zeroline=False,
                color="#cccccc"
            ),
            
            legend=dict(
                visible=True,
                orientation="h",
                yanchor="top",
                y=1.2,
                xanchor="right",
                x=1,
            ),
            colorway = ["#4DA3FF", "#FF6A3D", "#1F5FFF", "#C43A2F"]
        )
    )
    pio.templates["dark_dashboard"] = theme
    pio.templates.default = "plotly_dark+dark_dashboard"

def graph_individual_setting(fig, x_title, x_tickformat, y_title, y_tickprefix, y_tickformat):
    fig.update_xaxes(
        title = dict(text = x_title),
        tickformat=x_tickformat
    )
    fig.update_yaxes(
        title = dict(text = y_title),
        tickprefix=y_tickprefix,
        tickformat=y_tickformat,
    )
    return fig

def get_map_jp_to_en_sub_type(df_item_attribute):
    return dict(zip(
        df_item_attribute["項目"],
        df_item_attribute["英語名"]
    ))