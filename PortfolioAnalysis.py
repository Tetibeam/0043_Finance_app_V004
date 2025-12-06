# ポートフォリオ分析のグラフ

# インポート
import calPlot as cPlot
import calAnalysis as cAnsys
import calAnalysisIndex as cIdx
import dispSetting as dSet
import pandas as pd
import random
import datetime
import textwrap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from IPython.display import display
from dateutil.relativedelta import relativedelta

#####################################################################################
# 運用効率
#####################################################################################
# 資産ツリーマップ----------------------------------------------------------------
def disp_TotalAsset_Asset_Treemap(level):
    fig = go.Figure()
    dfA = cPlot.dfAssetPresent
    interval = 14
    weeks = dfA.index.max() - dfA.index.min()
    weeks = int(pd.Timedelta.to_pytimedelta(weeks).days / interval)
    cnt= weeks
    for i in range(0,weeks+1):
        index = (len(dfA)-1) - cnt*interval
        tsDate = dfA.index[index]
        strDate = pd.Timestamp.strftime(tsDate,"%Y-%m-%d")
        dfMap = cPlot.cal_TotalAsset_Tree_df(strDate)
        fig.add_trace(
            go.Treemap(
                name= '{:%y/%m/%d}'.format(tsDate),
                labels = dfMap.index,
                parents = dfMap["親クラス"],
                level=level,
                values = dfMap["割合"],
                visible=True,
                branchvalues ="total",
                root_color=dSet.ConstALL_bgcolor,
                marker_colorscale = 'Blues',
                customdata=dfMap["資産"],
                textinfo = "label+percent parent+percent entry",
                textfont_size= 16,
                hoverlabel_font_size = 16,
                hovertemplate =
                    '<br><i>Name</i>: ¥%{label}'+
                    '<br><i>Amount</i>: ¥%{customdata:,}<extra></extra>'
                )
            )
        cnt -= 1
    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[
                dict(visible=[False]* len(fig.data)),
                dict(title=fig.data[i].name),
                ],
            label=fig.data[i].name
            )
        step["args"][0]["visible"][i] = True
        steps.append(step)
    sliders = [dict(
        active=weeks,
        steps=steps,
        currentvalue=dict(
        #    visible=False,
                ),
        pad=dict(
            t=5, b=5, l=15,r=15
            )
        )]
    fig.update_layout(
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        width=None,
        height=None,
        margin=dict(l=10, r=10, t=20, b=0),
        sliders=sliders,
        #treemapcolorway = ["blue", "lightgray"],
        autosize = True,
        xaxis_rangeslider=dict(visible=False),
        )
    return fig
#display(disp_TotalAsset_Asset_Treemap("総資産"))

# 収益ツリーマップ-----------------------------------------------------------------
def disp_TotalProfit_Profit_Treemap(level):
    fig = go.Figure()
    dfP = cPlot.dfProfit
    interval = 14
    weeks = dfP.index.max() - dfP.index.min()
    weeks = int(pd.Timedelta.to_pytimedelta(weeks).days / interval)
    cnt= weeks
    for i in range(0,weeks+1):
        index = (len(dfP)-1) - cnt*interval
        tsDate = dfP.index[index]
        strDate = pd.Timestamp.strftime(tsDate,"%Y-%m-%d")
        dfMap = cAnsys.cal_TotalProfit_Tree_df(strDate)
        fig.add_trace(
            go.Treemap(
                name= '{:%y/%m/%d}'.format(tsDate),
                labels = dfMap.index,
                parents = dfMap["親クラス"],
                values = dfMap["割合"],
                level=level,
                marker=dict(
                    colors = dfMap["収益"],
                    colorscale = 'Blues',
                    colorbar=dict(
                        showticklabels=False,
                        ),
                    showscale = True
                    ),
                visible=True,
                branchvalues ="total",
                root_color=dSet.ConstALL_bgcolor,
                customdata=dfMap["収益"],
                textinfo = "label+percent parent+percent entry",
                textfont_size= 16,
                hoverlabel_font_size = 16,
                hovertemplate =
                    '<br><i>Name</i>: %{label}'+
                    '<br><i>Amount</i>: ¥%{customdata:,}<extra></extra>'
                    )
                )
        cnt -= 1
    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[
                dict(visible=[False]* len(fig.data)),
                dict(title=fig.data[i].name),
                ],
            label=fig.data[i].name
            )
        step["args"][0]["visible"][i] = True
        steps.append(step)
    sliders = [dict(
        active=weeks,
        steps=steps,
        currentvalue=dict(
            visible=False,
            ),
        pad=dict(
            t=5, b=5, l=15,r=15
            )
        )]
    fig.update_layout(
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        width=None,
        height=None,
        margin=dict(l=10, r=10, t=50, b=0),
        sliders=sliders,
        #treemapcolorway = ["blue", "lightgray"],
        autosize = True
        )
    return fig
#display(disp_TotalProfit_Profit_Treemap("総資産"))

# 選択項目の推移（資産、収益、収益率）-----------------------------------------------
def disp_TotalAsset_Asset_Treemap_Sub(assetName):
    dsA = cAnsys.cal_TreeClick_Asset(assetName).astype("int")
    dsP = cAnsys.cal_TreeClick_Profit(assetName).astype("int")
    dsPR = cAnsys.cal_TreeClick_ProfitRate(assetName)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes = "all",
        row_heights=[0.33,0.33,0.33],
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
        )
    fig.add_trace(go.Scatter(
        x=dsA.index, y=dsA,
        mode="lines",
        name="現在価値",
        customdata=[assetName]*len(dsA),
        #line=dict(color=dSet.dlColorS[6]),
        hovertemplate =
            '<br><i>x:y</i>:%{customdata}'+
            '<br><i>x</i>:%{x:"%Y/%m/%d"}'+
            '<br><i>y</i>:¥%{y:,}<extra></extra>',
        ),col=1,row=1)
    fig.update_yaxes(
        col=1,row=1,
        title="Amount",
        title_font_color="Grey",
        title_standoff=0,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )
    fig.add_trace(go.Scatter(
        x=dsP.index, y=dsP,
        mode="lines",
        name="収益",
        customdata=[assetName]*len(dsP),
        #line=dict(color=dSet.dlColorS[6]),
        hovertemplate =
            '<br><i>x:y</i>:%{customdata}'+
            '<br><i>x</i>:%{x:"%Y/%m/%d"}'+
            '<br><i>y</i>:¥%{y:,}<extra></extra>',
        ),col=1,row=2)
    fig.update_yaxes(
        col=1,row=2,
        title="Amount",
        title_font_color="Grey",
        title_standoff=0,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )
    fig.add_trace(go.Scatter(
        x=dsPR.index, y=dsPR,
        mode="lines",
        name="収益率",
        customdata=[assetName]*len(dsPR),
        #line=dict(color=dSet.dlColorS[6]),
        hovertemplate =
            '<br><i>x:y</i>:%{customdata}'+
            '<br><i>x</i>:%{x:"%Y/%m/%d"}'+
            '<br><i>y</i>:%{y:.2%}<extra></extra>',
        ),col=1,row=3)
    fig.update_yaxes(
        col=1,row=3,
        title="Rate",
        title_font_color="Grey",
        title_standoff=0,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".1%"
        )
    fig.update_xaxes(
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        tickformat="%y-%m",
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_layout(
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = True,
        legend=dict(
            font_size=10,
            title_side="top",
            x=0,y=1.05,
            xref="paper",yref="paper",
            orientation="h",
            ),
        autosize=True,
        )
    return fig

# 余裕資金-------------------------------------------------------------------------
def disp_BuyingPower():
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.5,0.5], row_heights=[0.5,0.5],
        horizontal_spacing=0.1,
        vertical_spacing=0.1,
        )
    # リスク資産配分率
    dsLsR = cPlot.cal_LiskAssetRatio()
    dsLsTR = cPlot.dfAssetTarget.loc[:dsLsR.index.max(), "リスク資産配分率"]
    fig.add_trace(
        go.Scatter(
            x=dsLsR.index, y=dsLsR,
            mode="lines", name="実績",
            line=dict(color=dSet.dlColorS[7]),
            hovertemplate =
                '<i>日付</i>:%{x:%Y/%m/%d}'+
                '<br><i>実績</i>:%{y:.1%}<extra></extra>'
            ),
            col=1,row=1,
        )
    fig.add_trace(
        go.Scatter(
            x=dsLsTR.index, y=dsLsTR,
            mode="lines", name="目標",
            line=dict(color=dSet.dlColorS[3],dash="dash"),
            hovertemplate =
                '<i>日付</i>:%{x:%Y/%m/%d}'+
                '<br><i>目標</i>:%{y:.1%}<extra></extra>'
            ),
            col=1,row=1,
        )
    fig.update_xaxes(
            col=1,row=1,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=dSet.ConstMS_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            tickformat="%y-%m",
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            )
    fig.update_yaxes(
            col=1,row=1,
            title="Rate",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=dSet.ConstMS_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            tickformat=".0%",
            ticklabelstandoff=0,
            )      
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.05, y=1.05,
        xanchor="left",
        font_size=14,
        text="リスク資産配分率",
        showarrow= False,
        col=1,row=1,        
        )
    # 生活資金
    df = cPlot.cal_LivingFunds_df()
    for column in df:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[column],stackgroup="one",
                mode="lines", name=column,
                line=dict(color=dSet.dlColorS[random.randint(3,8)]),
                customdata=[column]*len(df),
                hovertemplate =
                    '<br><i>名前</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>預金額</i>:¥%{y:,}<extra></extra>',
                ),
            col=2,row=1,
            )
    fig.update_xaxes(
        col=2,row=1,
        title="Date",
        title_standoff=0,
        tickfont=dict(size=dSet.ConstMS_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        tickformat="%y-%m",
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=2,row=1,
        title="Amount",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=dSet.ConstMS_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )      
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.05, y=1.05,
        xanchor="left",
        font_size=14,
        text="生活資金",
        showarrow= False,
        col=2,row=1,        
        )
    # 一般収支vs投資額(月毎)
    dsGbM = cPlot.cal_GeneralBarance_Monthly().astype("int")
    dsIvM = cAnsys.cal_InvestAmount_Monthly().astype("int")
    fig.add_trace(
            go.Scatter(
            x=dsGbM.index, y=dsGbM,
            mode="lines", name="一般収支",
            line=dict(color=dSet.dlColorS[7]),
            hovertemplate =
                '<i>日付</i>:%{x:%Y/%m/%d}'+
                '<br><i>一般収支</i>: ¥%{y:,}<extra></extra>'
            ),
            col=1,row=2,
        )
    fig.add_trace(
        go.Bar(
            x=dsIvM.index, y=dsIvM,
            name="投資額",
            marker=dict(color=dSet.dlColorS[4]),
            hovertemplate =
                '<i>日付</i>:%{x:%Y/%m}'+
                '<br><i>投資額</i>: ¥%{y:,}<extra></extra>'
            ),
            col=1,row=2,
        )
    fig.update_xaxes(
        col=1,row=2,
        title="Date",
        title_standoff=5,
        tickfont=dict(size=dSet.ConstItem_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
        range=(dSet.cal_XstartDate(),dSet.cal_XendDate()),
        mirror=True,
        tickformat="%y-%m",
        dtick="M1",
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=2,
        title="Amount",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=dSet.ConstItem_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )         
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.05, y=1.05,
        xanchor="left",
        font_size=14,
        text="一般収支と投資額",
        showarrow= False,
        col=1,row=2,        
        )
    # 1年間の償還日程
    df = cPlot.cal_Redemption_df()
    for column in df:
        fig.add_trace(
            go.Bar(
                x=df.index, y=df[column],
                name=column, showlegend=False,
                customdata=[column]*len(df),
                hovertemplate=
                    '<i>資産前</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>償還額</i>: ¥%{y:,}<extra></extra>',
                hoverlabel = dict(font_size=12),
                marker=dict(color=dSet.dlColorS[random.randint(3,len(dSet.dlColorS)-1)])
                ),
            col=2,row=2,
            )
    fig.update_xaxes(
        col=2,row=2,
        range=(datetime.date.today(), datetime.date.today()+relativedelta(years=1)),
        title="Date",
        title_standoff=5,
        tickfont=dict(size=dSet.ConstItem_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
        tickformat="%y-%m",
        dtick = 'M2',
        ticklabelstandoff=0
        )
    fig.update_yaxes(
        col=2,row=2,
        title="Amount",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=dSet.ConstMS_axis_tick_fontsize, color=dSet.ConstALL_axis_tick_color),
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )      
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.05, y=1.05,
        xanchor="left",
        font_size=14,
        text=" 年間償還総額: ¥"+ f'{int(df.sum(axis=1).max()):,}',
        showarrow= False,
        col=2,row=2,        
        )
    fig.update_layout(
        barmode="relative",
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
disp_BuyingPower()

# 運用効率----------------------------------------------------------------------
def disp_Efficiency():
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.33,0.33,0.34],
        vertical_spacing=0.075,
        )
    # 全体（収益/収益率/リスク）
    dfI = cAnsys.cal_InvestAmount_Class()
    dfI = dfI.loc[dfI.index.max()]
    dfP = cAnsys.cal_Profit_Class()
    dfP = dfP.loc[dfP.index.max()]
    dfPR = cAnsys.cal_ProfitRate_Class()
    dfPR = dfPR.loc[dfPR.index.max()]
    dfR = cAnsys.cal_LiskValue_Class()    
    fig.add_trace(
        go.Scatter(
            x=dfI, y=dfP,
            mode="markers",
            customdata = dfI.index,
            hovertemplate =
                '<br><i>資産区分</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>収益額</i>: %{y:,}<extra></extra>',
            marker=dict(
                color=dfP,
                size= 20,
                ),
            ),
        col=1,row=1,
        )
    fig.update_xaxes(
        col=1,row=1,
        title="Invest",
        title_standoff=0,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=1,
        title="Amount",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="投資効率（収益額）",
        showarrow= False,
        col=1,row=1,
        )
    
    fig.add_trace(
        go.Scatter(
            x=dfI, y=dfPR,
            mode="markers",
            customdata = dfI.index,
            hovertemplate =
                '<br><i>資産区分</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>収益率</i>: %{y:.2%}<extra></extra>',
            marker=dict(
                color=dfP,
                size= 20,
                ),
            ),
        col=1,row=2,
        )
    fig.update_xaxes(
        col=1,row=2,
        title="Invest",
        title_standoff=0,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=2,
        title="Rate",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".0%"
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="投資効率（収益率）",
        showarrow= False,
        col=1,row=2,
        )

    fig.add_trace(
        go.Scatter(
            x=dfI, y=dfR,
            mode="markers",
            customdata = dfI.index,
            hovertemplate =
                '<br><i>資産区分</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>リスク</i>: %{y:.2%}<extra></extra>',
            marker=dict(
                color=dfP,
                size= 20,
                ),
            ),
        col=1,row=3,
        )
    fig.update_xaxes(
        col=1,row=3,
        title="Invest",
        title_standoff=0,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=3,
        title="Lisk",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".2%"
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="投資効率（リスク）",
        showarrow= False,
        col=1,row=3,
        )

    fig.update_layout(
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    
    return fig
#display(disp_Efficiency())

##################################################################################
# ポートフォリオ分析
##################################################################################
# リスク＆リターン分析-------------------------------------------------------------
def disp_Lisk_Return():
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.5,0.5], row_heights=[0.5,0.5],
        specs=[
            [{"type":"domain"}, {"type":"xy"}],
            [{"type":"xy"}, {"type":"xy"}],
        ],
        shared_xaxes=True,
        )
    # リスク分布（ポートフォリオ別）
    df = cAnsys.cal_All_port()
    dfD = cAnsys.cal_All_port_divided()
    # 投資配分円グラフ
    fig.add_trace(
        go.Pie(
            labels=df.index,
            values=df["投資額"],
            showlegend=False,
            textinfo="label",
            hovertemplate =
                '<i>ポートフォリオ</i>:%{label}'+
                '<br><i>投資額</i>:¥%{value:,}'+
                '<br><i>割合</i>:%{percent:.1%}<extra></extra>',
            title=dict(text="投資配分", font_size=18),
            hole=0.4,
            visible=True,
            automargin=False,
            ),
            col=1,row=1,
        )
    fig.add_trace(
        go.Pie(
            labels=dfD.index,
            values=dfD["投資額"],
            showlegend=False,
            textinfo="label",
            hovertemplate =
                '<i>ポートフォリオ</i>:%{label}'+
                '<br><i>投資額</i>:¥%{value:,}'+
                '<br><i>割合</i>:%{percent:.1%}<extra></extra>',
            title=dict(text="投資配分", font_size=18),
            hole=0.4,
            visible=False,
            automargin=False,
            ),
            col=1,row=1,
        )
    # リスク
    fig.add_trace(
        go.Scatter(
            x=df["投資額"], y=df["リスク"],
            mode="markers",
            customdata = df.index,
            hovertemplate =
                '<br><i>ポートフォリオ</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
            marker=dict(
                size = dSet.set_MakerSize(df["収益"]),
                color = df["収益"],
                colorscale = "BlueRed",
                ),
            visible=True,
            ),
        col=2,row=1,
        )
    fig.add_trace(
        go.Scatter(
            x=dfD["投資額"], y=dfD["リスク"],
            mode="markers",
            customdata = dfD.index,
            hovertemplate =
                '<br><i>ポートフォリオ</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
            marker=dict(
                size = 14,
                color = dfD["収益率"],
                colorscale = "BlueRed",
                ),
            visible=False,
            ),
        col=2,row=1,
        )
    fig.update_xaxes(
        col=2,row=1,
        title="Invest",
        title_standoff=0,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=2,row=1,
        title="Lisk",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="リスク（ポートフォリオ別）",
        showarrow= False,
        col=2,row=1,
        )
    # 収益率
    fig.add_trace(
        go.Scatter(
            x=df["投資額"], y=df["収益率"],
            mode="markers",
            customdata = df.index,
            hovertemplate =
                '<br><i>ポートフォリオ</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>収益率</i>:%{y:.2%}<extra></extra>',
            marker=dict(
                size = dSet.set_MakerSize(df["収益"]),
                color = df["収益"],
                colorscale = "BlueRed",
                ),
            visible=True,
            ),
        col=2,row=2,
        )
    fig.add_trace(
        go.Scatter(
            x=dfD["投資額"], y=dfD["収益率"],
            mode="markers",
            customdata = dfD.index,
            hovertemplate =
                '<br><i>ポートフォリオ</i>:%{customdata}'+
                '<br><i>投資額</i>:¥%{x:,}'+
                '<br><i>収益率</i>:%{y:.2%}<extra></extra>',
            marker=dict(
                size = 14,
                color = dfD["収益率"],
                colorscale = "BlueRed",
                ),
            visible=False,
            ),
        col=2,row=2,
        )
    fig.update_xaxes(
        col=2,row=2,
        title="Invest",
        title_standoff=0,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=2,row=2,
        title="Rate",
        title_standoff=10,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".1%"
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="収益率",
        showarrow= False,
        col=2,row=2,
        )
    # リスク/収益率
    fig.add_trace(
        go.Scatter(
            x=df["リスク"], y=df["収益率"],
            mode="markers",
            customdata = df.index,
            hovertemplate =
                '<br><i>ポートフォリオ</i>:%{customdata}'+
                '<br><i>リスク</i>:%{x:.2f}'+
                '<br><i>収益率</i>:%{y:.2%}<extra></extra>',
            marker=dict(
                size = dSet.set_MakerSize(df["収益"]),
                color = df["収益"],
                colorscale = "BlueRed",
                ),
            visible=True,
            ),
        col=1,row=2,
        )
    fig.add_trace(
        go.Scatter(
            x=dfD["リスク"], y=dfD["収益率"],
            mode="markers",
            customdata = dfD.index,
            hovertemplate =
                '<br><i>ポートフォリオ</i>:%{customdata}'+
                '<br><i>リスク</i>:¥%{x:.2f}'+
                '<br><i>収益率</i>:%{y:.2%}<extra></extra>',
            marker=dict(
                size = 14,
                color = dfD["収益率"],
                colorscale = "BlueRed",
                ),
            visible=False,
            ),
        col=1,row=2,
        )
    fig.update_xaxes(
        col=1,row=2,
        title="Lisk",
        title_standoff=10,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=2,
        title="Rate",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".1%"
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="リスク/収益率",
        showarrow= False,
        col=1,row=2,
        )

    updatemenus = [
        dict(
            active=0,
            x=-0.1,
            xanchor="left",
            y=dSet.ConstMS_updatemenus_y,
            yanchor="top",
            direction="right",
            type="buttons",
            buttons=[
                dict(
                    label="バランスあり",
                    method="update",
                    args=[
                        dict(visible=[True, False] *4),
                        dict(
                            autosize=True
                            )
                        ]
                    ),
                dict(
                    label="バランスなし",
                    method="update",
                    args=[
                        dict(visible=[False, True] *4),
                        dict(
                            autosize=True
                            )
                        ]
                    ),
                ]
            )
        ]

    fig.update_layout(
        updatemenus = updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Lisk_Return())

def disp_Lisk_Return_click(portfolioType, label):
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.33,0.33,0.34],
        vertical_spacing=0.07,
        )
    # 収益率
    dfPR = cAnsys.cal_ProfitRate_port()
    dfPR_B = cAnsys.cal_ProfitRate_port_divided()
    # リスク
    dfL = cAnsys.cal_LiskValue_port_transition()
    dfL_B = cAnsys.cal_LiskValue_port_divided_transition()
    # 投資額
    dfI = cAnsys.cal_InvestAmount_port()
    dfI_B = cAnsys.cal_InvestAmount_port_divided()
    if portfolioType == "バランスあり":
        # 収益率
        fig.add_trace(
            go.Scatter(
                x=dfPR.index, y=dfPR[label],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                ),
                col=1,row=1,
            )
        fig.update_xaxes(
            col=1,row=1,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            tickformat="%m-%d"
            )
        fig.update_yaxes(
            col=1,row=1,
            title="Rate",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=14,
            text="収益率",
            showarrow= False,
            col=1,row=1,
            )
        # リスク
        fig.add_trace(
            go.Scatter(
                x=dfL.index, y=dfL[label],
                mode="lines", name="リスク",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
                ),
                col=1,row=2,
            )
        fig.update_xaxes(
            col=1,row=2,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            tickformat="%m-%d"
            )
        fig.update_yaxes(
            col=1,row=2,
            title="Lisk",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=14,
            text="リスク",
            showarrow= False,
            col=1,row=2,
            )
        # 投資額
        fig.add_trace(
            go.Scatter(
                x=dfI.index, y=dfI[label],
                mode="lines", name="投資額",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>投資額</i>:%{y:,}<extra></extra>',
                ),
                col=1,row=3,
            )
        fig.update_xaxes(
            col=1,row=3,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            tickformat="%m-%d"
            )
        fig.update_yaxes(
            col=1,row=3,
            title="Amount",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=14,
            text="投資額",
            showarrow= False,
            col=1,row=3,
            )
    elif portfolioType == "バランスなし":
        # 収益率
        fig.add_trace(
            go.Scatter(
                x=dfPR_B.index, y=dfPR_B[label],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:,}<extra></extra>',
                ),
                col=1,row=1,
            )
        fig.update_xaxes(
            col=1,row=1,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            tickformat="%m-%d"
            )
        fig.update_yaxes(
            col=1,row=1,
            title="Rate",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=14,
            text="収益率",
            showarrow= False,
            col=1,row=1,
            )
        # リスク
        fig.add_trace(
            go.Scatter(
                x=dfL_B.index, y=dfL_B[label],
                mode="lines", name="リスク",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
                ),
                col=1,row=2,
            )
        fig.update_xaxes(
            col=1,row=2,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            tickformat="%m-%d"
            )
        fig.update_yaxes(
            col=1,row=2,
            title="Lisk",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=14,
            text="リスク",
            showarrow= False,
            col=1,row=2,
            )
        # 投資額
        fig.add_trace(
            go.Scatter(
                x=dfI_B.index, y=dfI_B[label],
                mode="lines", name="投資額",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>投資額</i>:%{y:.1%}<extra></extra>',
                ),
                col=1,row=3,
            )
        fig.update_xaxes(
            col=1,row=3,
            title="Date",
            title_standoff=0,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            tickformat="%m-%d"
            )
        fig.update_yaxes(
            col=1,row=3,
            title="Amount",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=14,
            text="投資額",
            showarrow= False,
            col=1,row=3,
            )

    fig.update_layout(
        title = dict(
            text = label,
            font = dict(size = 16, color = dSet.ConstALL_title_color),
            xref = 'container',
            yref = "container",
            x = 0.05, y =0.99,
            xanchor = 'left',
            yanchor = 'top'
            ),
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Lisk_Return_click("バランスあり","クラウドファンディング"))

# インデックス相関------------------------------------------------------------------
def disp_Index_Corr():
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5,0.6],
        specs=[
            [{"type":"domain","colspan": 2},None],
            [{}, {}],
            ],
        )
    # インデックスの相関分布
    ddf = cAnsys.cal_Corr_Index_Port()
    for idx in ddf:
        fig.add_trace(
            go.Scatter(
                x=ddf[idx].index, y=ddf[idx],
                mode="markers",
                customdata = [idx] * len(ddf[idx]),
                hovertemplate =
                    '<i>ポートフォリオ</i>:%{x}'+
                    '<br><i>インデックス</i>:%{customdata}'+
                    '<br><i>相関係数</i>:%{y:.2f}<extra></extra>',
                visible=True,
                marker=dict(
                    size = 12,
                    color = ddf[idx],
                    cmin = -1,
                    cmax = 1,
                    cmid = 0,
                    colorscale = "BlueRed",
                    ),
                ),
            col=1,row=2,
            )
    fig.update_xaxes(
        col=1,row=2,
        #title="Portfolio",
        #title_standoff=10,
        tickfont=dict(size=14, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=2,
        title="Corr",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        range=(-1,1)
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.18,
        xanchor="center",
        font_size=16,
        text="相関係数分布（ポートフォリオ）",
        showarrow= False,
        col=1,row=2,
        )
    dds = cAnsys.cal_Corr_Index_Index()
    for idx in dds:
        fig.add_trace(
            go.Scatter(
                x=dds[idx].index, y=dds[idx],
                mode="markers",
                customdata=[ idx] * len(dds[idx]),
                hovertemplate = 
                    '<i>インデックス</i>:%{x}'+
                    '<br><i>相関係数</i>:%{y:.2f}<extra></extra>',
                visible=True,
                marker=dict(
                    size = 12,
                    color = dds[idx],
                    cmin = -1,
                    cmax = 1,
                    cmid = 0,
                    colorscale = "BlueRed",
                    ),
                ),
            col=2,row=2,
            )
    fig.update_xaxes(
        col=2,row=2,
        #title="Portfolio",
        #title_standoff=10,
        tickfont=dict(size=14, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        showticklabels =False
        )
    fig.update_yaxes(
        col=2,row=2,
        title="Corr",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        range=(-1,1)
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.18,
        xanchor="center",
        font_size=16,
        text="相関係数分布（インデックス）",
        showarrow= False,
        col=2,row=2,
        )
    ####
    buttons = []
    i=0
    for idx in ddf:
        button = dict(
            args=[dict(visible=[False] * len(fig.data))],
            method="restyle",
            label=idx,
            )
        button["args"][0]["visible"][i]=True
        button["args"][0]["visible"][i+20]=True
        buttons.append(button)
        i+=1
    button = dict(
        args=[dict(visible=[True] * len(fig.data))],
        method="restyle",
        label="ALL",
        )
    buttons.append(button)
    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.5,y=0.56,
        xanchor="center",yanchor="top",
        ),]
    ######
    df = cAnsys.cal_port_Corr_MaxMin()
    header = ["ポートフォリオ"] + df.columns.tolist()
    cells =  [[None,None,None],[None,None,None]]
    cells =  [[None]*len(df.index), [None]*len(df.index), [None]*len(df.index), [None]*len(df.index), [None]*len(df.index),\
    [None]*len(df.index), [None]*len(df.index)]
    i=0;j=1
    for port in df.index:
        cells[0][i] = port
        for column in df:
            cells[j][i] = df.loc[port, column]
            j+=1
        i+=1
        j=1
    fig.add_trace(
        go.Table(
            columnwidth=[18,33,13,33,13,33,12],
            header=dict(
                values=header,
                line_color='rgb(247,251,255)',
                fill_color='rgb(8,81,156)',
                align=['center'],
                font=dict(color='white', size=12),
                height=25
                ),
            cells=dict(
                values=cells,
                line_color='rgb(247,251,255)',
                fill=dict(color=['rgb(158,202,225)', 'rgb(222,235,247)']),
                align=['center',"right"],
                font=dict(color='black', size=12),
                height=25,
                )
            ),
        col=1,row=1,
        )
    fig.update_layout(
        updatemenus = updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Index_Corr())

def disp_Index_Corr_click(port, index):
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.33,0.33,0.34],
        vertical_spacing=0.06,
        specs=[
            [{"secondary_y":True}],
            [{"secondary_y":True}],
            [{"secondary_y":False}],
            ],
        )
    dfPR = cAnsys.cal_ProfitRate_port()
    if port in dfPR.columns:
        # top クリックした xy の推移  
        fig.add_trace(
            go.Scatter(
                x=dfPR.index, y=dfPR[port],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                customdata=[port]*len(dfPR[port]),
                hovertemplate =
                    '<i>ポートフォリオ</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                ),
                secondary_y=False,
                col=1,row=1,
            )
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[index],
                mode="lines", name="インデックス",
                line=dict(color=dSet.dlColorS[3]),
                customdata=[index]*len(cIdx.dfIdx[index]),
                hovertemplate =
                    '<i>インデックス</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                ),
                secondary_y=True,
                col=1,row=1,
            )
        fig.update_xaxes(
                col=1,row=1,
                #title="Date",
                #title_standoff=0,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                mirror=True,
                title_font_color = dSet.ConstALL_axis_tick_color,
                title_font_size = 10,
                ticklabelstandoff=0,
                gridcolor="white", gridwidth=1, griddash="solid",
                tickformat="%m-%d"
                )
        fig.update_yaxes(
            col=1,row=1,
            secondary_y=False,
            title="Rate",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.update_yaxes(
            col=1,row=1,
            secondary_y=True,
            title="Index",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            #gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=False,
            mirror=False,
            ticklabelstandoff=0,
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.15,
            xanchor="center",
            font_size=12,
            text= port+" vs "+index,
            showarrow= False,
            col=1,row=1,
            )
        # mid クリックした xとdropdown（ポートフォリオ）の推移
        fig.add_trace(
            go.Scatter(
                x=dfPR.index, y=dfPR[port],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                customdata=[port]*len(dfPR[port]),
                hovertemplate =
                    '<i>ポートフォリオ</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                ),
                secondary_y=False,
                col=1,row=2,
            )
        for dPort in dfPR:   
            fig.add_trace(
                go.Scatter(
                    x=dfPR.index, y=dfPR[dPort],
                    mode="lines", name="収益率",
                    line=dict(color=dSet.dlColorS[3]),
                    customdata=[dPort]*len(dfPR[dPort]),
                    hovertemplate =
                        '<i>ポートフォリオ</i>:%{customdata}'+
                        '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                        '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                    visible=False,
                    ),
                    secondary_y=False,
                    col=1,row=2,
                )
        fig.update_xaxes(
                col=1,row=2,
                #title="Date",
                #title_standoff=0,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                mirror=True,
                title_font_color = dSet.ConstALL_axis_tick_color,
                title_font_size = 10,
                ticklabelstandoff=0,
                gridcolor="white", gridwidth=1, griddash="solid",
                tickformat="%m-%d"
                )
        fig.update_yaxes(
            col=1,row=2,
            secondary_y=False,
            title="Rate",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=12,
            text=port+" vs ポートフォリオ",
            showarrow= False,
            col=1,row=2,
            )
    else:
        # top クリックした xy の推移  
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[port],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                customdata=[port]*len(cIdx.dfIdx[port]),
                hovertemplate =
                    '<i>インデックス</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:}<extra></extra>',
                ),
                secondary_y=False,
                col=1,row=1,
            )
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[index],
                mode="lines", name="インデックス",
                line=dict(color=dSet.dlColorS[3]),
                customdata=[index]*len(cIdx.dfIdx[index]),
                hovertemplate =
                    '<i>インデックス</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:}<extra></extra>',
                ),
                secondary_y=True,
                col=1,row=1,
            )
        fig.update_xaxes(
                col=1,row=1,
                #title="Date",
                #title_standoff=0,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                mirror=True,
                title_font_color = dSet.ConstALL_axis_tick_color,
                title_font_size = 10,
                ticklabelstandoff=0,
                gridcolor="white", gridwidth=1, griddash="solid",
                tickformat="%m-%d"
                )
        fig.update_yaxes(
            col=1,row=1,
            secondary_y=False,
            title="Index",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            )
        fig.update_yaxes(
            col=1,row=1,
            secondary_y=True,
            title="Index",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            #gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=False,
            mirror=False,
            ticklabelstandoff=0,
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.15,
            xanchor="center",
            font_size=12,
            text=port+" vs "+index,
            showarrow= False,
            col=1,row=1,
            )
        # mid クリックした xとdropdown（ポートフォリオ）の推移
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[port],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                customdata=[port]*len(cIdx.dfIdx[port]),
                hovertemplate =
                    '<i>インデックス</i>:%{customdata}'+
                    '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:}<extra></extra>',
                ),
                secondary_y=False,
                col=1,row=2,
            )
        for dPort in dfPR:   
            fig.add_trace(
                go.Scatter(
                    x=dfPR.index, y=dfPR[dPort],
                    mode="lines", name="収益率",
                    line=dict(color=dSet.dlColorS[3]),
                    customdata=[dPort]*len(dfPR[dPort]),
                    hovertemplate =
                        '<i>ポートフォリオ</i>:%{customdata}'+
                        '<br><i>日付</i>:%{x:%Y/%m/%d}'+
                        '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                    visible=False,
                    ),
                    secondary_y=True,
                    col=1,row=2,
                )
        fig.update_xaxes(
                col=1,row=2,
                #title="Date",
                #title_standoff=0,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                mirror=True,
                title_font_color = dSet.ConstALL_axis_tick_color,
                title_font_size = 10,
                ticklabelstandoff=0,
                gridcolor="white", gridwidth=1, griddash="solid",
                tickformat="%m-%d"
                )
        fig.update_yaxes(
            col=1,row=2,
            secondary_y=False,
            title="Index",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            )
        fig.update_yaxes(
            col=1,row=2,
            secondary_y=True,
            title="Index",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            tickformat=".1%"
            )
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=0.5, y=1.05,
            xanchor="center",
            font_size=12,
            text=port+" vs ポートフォリオ",
            showarrow= False,
            col=1,row=2,
            )
       # bottom クリックしたx（ポートフォリオだったら）のポートフォリオの相関分布
    dds = cAnsys.cal_Corr_Port_Port()
    for dPort in dds:
        fig.add_trace(
            go.Scatter(
                x=dds[dPort].index, y=dds[dPort],
                mode="markers",
                hovertemplate =
                    '<i>ポートフォリオ</i>:%{x:%Y/%m/%d}'+
                    '<br><i>相関係数</i>:%{y:.2f}<extra></extra>',
                marker=dict(size=12),
                visible=False,
                ),
                secondary_y=False,
                col=1,row=3,
            )
    fig.update_xaxes(
        col=1,row=3,
        #title="Portfolio",
        #title_standoff=10,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        title_font_size = 10,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        showticklabels =False
        )
    fig.update_yaxes(
        col=1,row=3,
        title="Corr",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        title_font_size = 10,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        range=(-1,1)
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=12,
        text="相関係数分布",
        showarrow= False,
        col=1,row=3,
        )
    # dropdown
    buttons = []
    i=0
    for dPort in dfPR:
        button = dict(
            args=[dict(visible=[False] * len(fig.data))],
            method="restyle",
            label=dPort,
            )
        button["args"][0]["visible"][0]=True
        button["args"][0]["visible"][1]=True
        button["args"][0]["visible"][2]=True
        button["args"][0]["visible"][3+i]=True
        button["args"][0]["visible"][3+i+11]=True
        buttons.append(button)
        i+=1
    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.5,y=1.1,
        xanchor="center",yanchor="top",
        ),]
    fig.update_layout(
        updatemenus=updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Index_Corr_click("TOPIX","日経平均"))
##################################################################################
# 銘柄分析
##################################################################################
# 投信銘柄-------------------------------------------------------------
def disp_Invest_LiskReturn_Asset():
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.5,0.5],
        specs=[
            [{"type":"domain"}, {"type":"xy"}]
            ]
        )
    ddf = cAnsys.cal_All_toPort()
    df = cAnsys.cal_All_port()
    # 投資配分円グラフ
    fig.add_trace(
        go.Pie(
            labels=df.index,
            values=df["投資額"],
            showlegend=False,
            textinfo="label",
            textposition="outside",
            hovertemplate =
                '<i>ポートフォリオ</i>:%{label}'+
                '<br><i>投資額</i>:¥%{value:,}'+
                '<br><i>割合</i>:%{percent:.1%}<extra></extra>',
            title=dict(text="投資配分", font_size=18),
            hole=0.4,
            visible=True,
            automargin=False,
            ),
            col=1,row=1,
        )
    text = []
    for port in ddf:
        text = ddf[port].index.str.slice(0, 12)
        fig.add_trace(
            go.Pie(
                labels=ddf[port].index,
                values=ddf[port]["投資額"],
                showlegend=False,
                text=text,
                textinfo="text",
                textposition="outside",
                hovertemplate =
                    '<i>銘柄</i>:%{label}'+
                    '<br><i>投資額</i>:¥%{value:,}'+
                    '<br><i>割合</i>:%{percent:.1%}<extra></extra>',
                title=dict(text="投資配分", font_size=18),
                hole=0.4,
                visible=False,
                automargin=False,
                ),
                col=1,row=1,
            )
     # リスク/収益率
    for port in ddf:
        fig.add_trace(
            go.Scatter(
                x=ddf[port]["リスク"], y=ddf[port]["収益率"],
                mode="markers",
                customdata = ddf[port].index,
                hovertemplate =
                    '<br><i>銘柄</i>:%{customdata}'+
                    '<br><i>リスク</i>:%{x:.2f}'+
                    '<br><i>収益率</i>:%{y:.2%}<extra></extra>',
                marker=dict(
                    size = dSet.set_MakerSize(ddf[port]["収益"]),
                    color = ddf[port]["収益"],
                    colorscale = "BlueRed",
                    cmid=0,
                    ),
                visible=True,
                ),
            col=2,row=1,
            )
    fig.update_xaxes(
        col=2,row=1,
        title="Lisk",
        title_standoff=10,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=2,row=1,
        title="Rate",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".1%"
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="リスク/収益率",
        showarrow= False,
        col=2,row=1,
        )

    buttons = []
    i=0
    for idx in ddf:
        button = dict(
            args=[dict(visible=[False] * len(fig.data))],
            method="restyle",
            label=idx,
            )
        button["args"][0]["visible"][1+i]=True
        button["args"][0]["visible"][1+i+11]=True
        buttons.append(button)
        i+=1
    button = dict(
        args=[dict(visible=[True] * len(fig.data))],
        method="restyle",
        label="ALL",
        )
    for i in range(len(ddf)):
        button["args"][0]["visible"][1+i]=False
    buttons.append(button)

    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0,y=1.15,
        xanchor="center",yanchor="top",
        ),]
    fig.update_layout(
        updatemenus = updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )

    return fig
#display(disp_Invest_LiskReturn_Asset())

def disp_Lisk_Return_Asset():
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.5,0.5],
        shared_xaxes=True,
        )
    ddf = cAnsys.cal_All_toPort()
    # リスク
    for port in ddf:
        fig.add_trace(
            go.Scatter(
                x=ddf[port]["投資額"], y=ddf[port]["リスク"],
                mode="markers",
                customdata = ddf[port].index,
                hovertemplate =
                    '<br><i>銘柄</i>:%{customdata}'+
                    '<br><i>投資額</i>:¥%{x:,}'+
                    '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
                marker=dict(
                    size = dSet.set_MakerSize(ddf[port]["収益"]),
                    color = ddf[port]["収益"],
                    colorscale = "BlueRed",
                    cmid=0,
                    ),
                visible=True,
                ),
            col=2,row=1,
            )
    fig.update_xaxes(
        col=2,row=1,
        title="Invest",
        title_standoff=10,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=2,row=1,
        title="Lisk",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="リスク",
        showarrow= False,
        col=2,row=1,
        )

    # 収益率
    for port in ddf:
        fig.add_trace(
            go.Scatter(
                x=ddf[port]["投資額"], y=ddf[port]["収益率"],
                mode="markers",
                customdata = ddf[port].index,
                hovertemplate =
                    '<br><i>銘柄</i>:%{customdata}'+
                    '<br><i>投資額</i>:¥%{x:,}'+
                    '<br><i>収益率</i>:%{y:.2%}<extra></extra>',
                marker=dict(
                    size = dSet.set_MakerSize(ddf[port]["収益"]),
                    color = ddf[port]["収益"],
                    colorscale = "BlueRed",
                    cmid=0,
                    ),
                visible=True,
                ),
            col=1,row=1,
            )
    fig.update_xaxes(
        col=1,row=1,
        title="Invest",
        title_standoff=10,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        )
    fig.update_yaxes(
        col=1,row=1,
        title="Rate",
        title_standoff=10,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        tickformat=".1%"
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=14,
        text="収益率",
        showarrow= False,
        col=1,row=1,
        )
   
    buttons = []
    i=0
    for idx in ddf:
        button = dict(
            args=[dict(visible=[False] * len(fig.data))],
            method="restyle",
            label=idx,
            )
        button["args"][0]["visible"][i]=True
        button["args"][0]["visible"][i+11]=True
        buttons.append(button)
        i+=1
    button = dict(
        args=[dict(visible=[True] * len(fig.data))],
        method="restyle",
        label="ALL",
        )
    buttons.append(button)

    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0,y=1.15,
        xanchor="center",yanchor="top",
        ),]
    fig.update_layout(
        updatemenus = updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Lisk_Return_Asset())

def disp_Lisk_Return_Asset_click(portfolioType, label):
    fig = go.Figure()
    # 収益率
    dfPR = cAnsys.cal_ProfitRate()
    dfPR_port = cAnsys.cal_ProfitRate_port()
    # 収益額
    dfP = cAnsys.cal_Profit()
    dfP_port = cAnsys.cal_Profit_port()
    if portfolioType == "銘柄":
        # 収益率
        fig.add_trace(
            go.Scatter(
                x=dfPR.index, y=dfPR[label],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                visible=False,
                ),
            )
        # 収益額
        fig.add_trace(
            go.Scatter(
                x=dfP.index, y=dfP[label],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益額</i>:%{y:.1%}<extra></extra>',
                visible=False,
                ),
            )
    elif portfolioType == "ポートフォリオ":
        # 収益率
        fig.add_trace(
            go.Scatter(
                x=dfPR_port.index, y=dfPR_port[label],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益率</i>:%{y:,}<extra></extra>',
                visible=False,
                ),
            )
        # 収益額
        fig.add_trace(
            go.Scatter(
                x=dfP_port.index, y=dfP_port[label],
                mode="lines", name="収益率",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>収益額</i>:%{y:.1%}<extra></extra>',
                visible=False,
                ),
            )
    updatemenus = [
        dict(
            active=0,
            x=0.99,
            xanchor="right",
            y=1.09,
            yanchor="top",
            direction="right",
            type="buttons",
            buttons=[
                dict(
                    label="収益率",
                    method="update",
                    args=[
                        dict(visible=[True, False]),
                        dict(
                            xaxis=dict(
                                title="Date",
                                title_standoff=0,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                mirror=True,
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                ticklabelstandoff=0,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                tickformat="%m-%d"
                                ),
                            yaxis=dict(
                                title="Lisk",
                                title_standoff=5,
                                fixedrange=False,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                showspikes=True,
                                mirror=True,
                                ticklabelstandoff=0,
                                tickformat=".1%",
                                ),
                            autosize=True,
                            )
                        ]
                    ),
                dict(
                    label="収益額",
                    method="update",
                    args=[
                        dict(visible=[False, True]),
                        dict(
                            xaxis=dict(
                                title="Date",
                                title_standoff=0,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                mirror=True,
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                ticklabelstandoff=0,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                tickformat="%m-%d"
                                ),
                            yaxis=dict(
                                title="Lisk",
                                title_standoff=5,
                                fixedrange=False,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                showspikes=True,
                                mirror=True,
                                ticklabelstandoff=0,
                                tickformat="",
                                ),
                            autosize=True,
                            )
                        ]
                    ),
                ]
            )
        ]

    fig.update_layout(
        title = dict(
            text = label,
            font = dict(size = 14, color = dSet.ConstALL_title_color),
            xref = 'container',
            yref = "container",
            x = 0.5, y =0.98,
            xanchor = 'center',
            yanchor = 'top'
            ),
        updatemenus=updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Lisk_Return_Asset_click("銘柄","⼝座残⾼(オルタナバンク)"))

def disp_Lisk_Return_Asset_click2(portfolioType, label):
    fig = go.Figure()
    # リスク
    dfL = cAnsys.cal_LiskValue_transition()
    dfL_port = cAnsys.cal_LiskValue_port_transition()
    # 投資額
    dfI = cAnsys.cal_InvestAmount()
    dfI_port = cAnsys.cal_InvestAmount_port()
    if portfolioType == "銘柄":
        # リスク
        fig.add_trace(
            go.Scatter(
                x=dfL.index, y=dfL[label],
                mode="lines", name="リスク",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
                visible=False,
                ),
            )
        # 投資額
        fig.add_trace(
            go.Scatter(
                x=dfI.index, y=dfI[label],
                mode="lines", name="投資額",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>投資額</i>:%{y:,}<extra></extra>',
                visible=False,
                ),
            )
    elif portfolioType == "ポートフォリオ":
        # リスク
        fig.add_trace(
            go.Scatter(
                x=dfL_port.index, y=dfL_port[label],
                mode="lines", name="リスク",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>リスク</i>:%{y:.1%}<extra></extra>',
                visible=False,
                ),
            )
        # 投資額
        fig.add_trace(
            go.Scatter(
                x=dfI_port.index, y=dfI_port[label],
                mode="lines", name="投資額",
                line=dict(color=dSet.dlColorS[7]),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>投資額</i>:%{y:.1%}<extra></extra>',
                visible=False,
                ),
            )

    updatemenus = [
        dict(
            active=0,
            x=0.99,
            xanchor="right",
            y=1.09,
            yanchor="top",
            direction="right",
            type="buttons",
            buttons=[
                dict(
                    label="リスク",
                    method="update",
                    args=[
                        dict(visible=[True, False]),
                        dict(
                            xaxis=dict(
                                title="Date",
                                title_standoff=0,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                mirror=True,
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                ticklabelstandoff=0,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                tickformat="%m-%d"
                                ),
                            yaxis=dict(
                                title="Lisk",
                                title_standoff=5,
                                fixedrange=False,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                showspikes=True,
                                mirror=True,
                                ticklabelstandoff=0,
                                tickformat=".1%",
                                ),
                            autosize=True,
                            )
                        ]
                    ),
                dict(
                    label="投資額",
                    method="update",
                    args=[
                        dict(visible=[False, True]),
                        dict(
                            xaxis=dict(
                                title="Date",
                                title_standoff=0,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                mirror=True,
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                ticklabelstandoff=0,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                tickformat="%m-%d"
                                ),
                            yaxis=dict(
                                title="Lisk",
                                title_standoff=5,
                                fixedrange=False,
                                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                                title_font_color = dSet.ConstALL_axis_tick_color,
                                gridcolor="white", gridwidth=1, griddash="solid",
                                showspikes=True,
                                mirror=True,
                                ticklabelstandoff=0,
                                tickformat="",
                                ),
                            autosize=True,
                            )
                        ]
                    ),
                ]
            )
        ]
    fig.update_layout(
        title = dict(
            text = label,
            font = dict(size = 14, color = dSet.ConstALL_title_color),
            xref = 'container',
            yref = "container",
            x = 0.5, y =0.98,
            xanchor = 'center',
            yanchor = 'top'
            ),
        updatemenus=updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Lisk_Return_Asset_click2("銘柄","⼝座残⾼(オルタナバンク)"))

# 銘柄相関---------------------------------------------------------------
def disp_Index_Corr_Asset_table():
    fig = go.Figure()
    ddf = cAnsys.cal_Corr_MaxMin_toPort()
    for port in ddf:
        header = ["銘柄"] + ddf[port].columns.tolist()
        #cells =  [[None,None,None],[None,None,None]]
        cells =  [[None]*len(ddf[port].index), [None]*len(ddf[port].index), [None]*len(ddf[port].index), [None]*len(ddf[port].index),\
        [None]*len(ddf[port].index), [None]*len(ddf[port].index), [None]*len(ddf[port].index)]
        i=0;j=1
        for asset in ddf[port].index:
            cells[0][i] = asset
            for column in ddf[port]:
                cells[j][i] = ddf[port].loc[asset, column]
                j+=1
            i+=1
            j=1
        fig.add_trace(
            go.Table(
                columnwidth=[50,33,13,33,13,33,12],
                header=dict(
                    values=header,
                    line_color='rgb(247,251,255)',
                    fill_color='rgb(8,81,156)',
                    align=['center'],
                    font=dict(color='white', size=12),
                    height=25
                    ),
                cells=dict(
                    values=cells,
                    line_color='rgb(247,251,255)',
                    fill=dict(color=['rgb(158,202,225)', 'rgb(222,235,247)']),
                    align=['center',"right"],
                    font=dict(color='black', size=12),
                    height=25,
                    ),
                visible=False,
                ),
            )

    buttons = []
    i=0
    for port in ddf:
        button = dict(
            args=[dict(visible=[False] * len(fig.data))],
            method="restyle",
            label=port,
            )
        button["args"][0]["visible"][i]=True
        buttons.append(button)
        i+=1
    button = dict(
        args=[dict(visible=[True] * len(fig.data))],
        method="restyle",
        label="ALL",
        )
    buttons.append(button)

    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.05,y=1.15,
        xanchor="center",yanchor="top",
        ),]

    fig.update_layout(
        updatemenus = updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    return fig
#display(disp_Index_Corr_Asset_table())

def disp_Index_Corr_Asset(dlVisible):
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.5,0.5],
        )
    # インデックスの相関分布
    ddf = cAnsys.cal_Corr_Index_toPort()
    i=0
    for port in ddf:
        if dlVisible[i]:
            visiblePort = port
        i+=1
    for idx in ddf[visiblePort]:
        fig.add_trace(
            go.Scatter(
                x=ddf[visiblePort][idx].index, y=ddf[visiblePort][idx],
                mode="markers",
                customdata = [idx] * len(ddf[visiblePort][idx]),
                hovertemplate =
                    '<i>銘柄</i>:%{x}'+
                    '<br><i>インデックス</i>:%{customdata}'+
                    '<br><i>相関係数</i>:%{y:.2f}<extra></extra>',
                visible=False,
                marker=dict(
                    size = 12,
                    color = ddf[visiblePort][idx],
                    cmin = -1,
                    cmax = 1,
                    cmid = 0,
                    colorscale = "BlueRed",
                    ),
                ),
            col=1,row=1,
            )
    fig.update_xaxes(
        col=1,row=1,
        tickfont=dict(size=14, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        showticklabels =False,
        )
    fig.update_yaxes(
        col=1,row=1,
        title="Corr",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        range=(-1,1)
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=16,
        text="相関係数分布",
        showarrow= False,
        col=1,row=1,
        )
    
    dds = cAnsys.cal_Corr_Index_Index()
    for idx in dds:
        fig.add_trace(
            go.Scatter(
                x=dds[idx].index, y=dds[idx],
                mode="markers",
                customdata=[ idx] * len(dds[idx]),
                hovertemplate = 
                    '<i>インデックス</i>:%{x}'+
                    '<br><i>相関係数</i>:%{y:.2f}<extra></extra>',
                visible=True,
                marker=dict(
                    size = 12,
                    color = dds[idx],
                    cmin = -1,
                    cmax = 1,
                    cmid = 0,
                    colorscale = "BlueRed",
                    ),
                ),
            col=2,row=1,
            )
    fig.update_xaxes(
        col=2,row=1,
        #title="Portfolio",
        #title_standoff=10,
        tickfont=dict(size=14, color=dSet.ConstALL_axis_tick_color),
        mirror=True,
        title_font_color = dSet.ConstALL_axis_tick_color,
        ticklabelstandoff=0,
        gridcolor="white", gridwidth=1, griddash="solid",
        showticklabels =False
        )
    fig.update_yaxes(
        col=2,row=1,
        title="Corr",
        title_standoff=5,
        fixedrange=False,
        tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
        title_font_color = dSet.ConstALL_axis_tick_color,
        gridcolor="white", gridwidth=1, griddash="solid",
        showspikes=True,
        mirror=True,
        ticklabelstandoff=0,
        range=(-1,1)
        )
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.5, y=1.05,
        xanchor="center",
        font_size=16,
        text="相関係数分布（インデックス）",
        showarrow= False,
        col=2,row=1,
        )
    
    buttons = []
    i=0
    for idx in ddf[visiblePort]:
        button = dict(
            args=[dict(visible=[False] * len(fig.data))],
            method="restyle",
            label=idx,
            )
        button["args"][0]["visible"][i]=True
        button["args"][0]["visible"][i+20]=True
        buttons.append(button)
        i+=1
    button = dict(
        args=[dict(visible=[True] * len(fig.data))],
        method="restyle",
        label="ALL",
        )
    buttons.append(button)
    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.05,y=1.17,
        xanchor="center",yanchor="top",
        )]

    fig.update_layout(
        updatemenus = updatemenus,
        width=None,
        height=None,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor=dSet.ConstALL_bgcolor,
        plot_bgcolor=dSet.ConstALL_bgcolor,
        showlegend = False,
        autosize=True,
        )
    
    return fig
#display(disp_Index_Corr_Asset())

def disp_Corr_Lisk_Return_Asset_click(asset, index):
    fig = go.Figure()
    dfPR = cAnsys.cal_ProfitRate()
    if asset in dfPR.columns:
        # 収益率
        fig.add_trace(
            go.Scatter(
                x=dfPR.index, y=dfPR[asset],
                mode="lines", name=asset,
                line=dict(color=dSet.dlColorS[7]),
                customdata=[index]*len(cIdx.dfIdx),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>インデックス</i>:%{customdata}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                #yaxis="y1",
                ),
            )
        # インデックス
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[index],
                mode="lines", name=index,
                line=dict(color=dSet.dlColorS[4]),
                customdata=[index]*len(cIdx.dfIdx),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>インデックス</i>:%{customdata}'+
                    '<br><i>インデックス値</i>:%{y:.}<extra></extra>',
                yaxis="y2",
                ),
            )
        fig.update_layout(
            title = dict(
                text = asset,
                font = dict(size = 14, color = dSet.ConstALL_title_color),
                xref = 'container',
                yref = "container",
                x = 0.5, y =0.98,
                xanchor = 'center',
                yanchor = 'top'
                ),
            width=None,
            height=None,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor=dSet.ConstALL_bgcolor,
            plot_bgcolor=dSet.ConstALL_bgcolor,
            showlegend = False,
            autosize=True,
            xaxis=dict(
                title="Date",
                title_standoff=10,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                mirror=True,
                title_font_color = dSet.ConstALL_axis_tick_color,
                ticklabelstandoff=0,
                gridcolor="white", gridwidth=1, griddash="solid",
                tickformat="%m-%d"
                ),
            yaxis=dict(
                side='left',
                title="Rate",
                title_standoff=5,
                fixedrange=False,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                title_font_color = dSet.ConstALL_axis_tick_color,
                #gridcolor="white", gridwidth=1, griddash="solid",
                #showspikes=True,
                mirror=True,
                ticklabelstandoff=0,
                tickformat=".1%",
                ),
            yaxis2=dict(
                side='right',
                showgrid=False,
                title="Index",
                title_standoff=5,
                fixedrange=False,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                title_font_color = dSet.ConstALL_axis_tick_color,
                #gridcolor="white", gridwidth=1, griddash="solid",
                #showspikes=True,
                mirror=True,
                ticklabelstandoff=0,
                tickformat=",",
                overlaying='y',
                )
            )
    else:
        # 収益率
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[asset],
                mode="lines", name=asset,
                line=dict(color=dSet.dlColorS[7]),
                customdata=[index]*len(cIdx.dfIdx),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>インデックス</i>:%{customdata}'+
                    '<br><i>収益率</i>:%{y:.1%}<extra></extra>',
                #yaxis="y1",
                ),
            )
        # インデックス
        fig.add_trace(
            go.Scatter(
                x=cIdx.dfIdx.index, y=cIdx.dfIdx[index],
                mode="lines", name=index,
                line=dict(color=dSet.dlColorS[4]),
                customdata=[index]*len(cIdx.dfIdx),
                hovertemplate =
                    '<i>日付</i>:%{x:%Y/%m/%d}'+
                    '<br><i>インデックス</i>:%{customdata}'+
                    '<br><i>インデックス値</i>:%{y:.}<extra></extra>',
                yaxis="y2",
                ),
            )
        fig.update_layout(
            title = dict(
                text = asset,
                font = dict(size = 14, color = dSet.ConstALL_title_color),
                xref = 'container',
                yref = "container",
                x = 0.5, y =0.98,
                xanchor = 'center',
                yanchor = 'top'
                ),
            width=None,
            height=None,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor=dSet.ConstALL_bgcolor,
            plot_bgcolor=dSet.ConstALL_bgcolor,
            showlegend = False,
            autosize=True,
            xaxis=dict(
                title="Date",
                title_standoff=10,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                mirror=True,
                title_font_color = dSet.ConstALL_axis_tick_color,
                ticklabelstandoff=0,
                gridcolor="white", gridwidth=1, griddash="solid",
                tickformat="%m-%d"
                ),
            yaxis=dict(
                side='left',
                title="Index",
                title_standoff=5,
                fixedrange=False,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                title_font_color = dSet.ConstALL_axis_tick_color,
                #gridcolor="white", gridwidth=1, griddash="solid",
                #showspikes=True,
                mirror=True,
                ticklabelstandoff=0,
                tickformat=",",
                ),
            yaxis2=dict(
                side='right',
                showgrid=False,
                title="Index",
                title_standoff=5,
                fixedrange=False,
                tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
                title_font_color = dSet.ConstALL_axis_tick_color,
                #gridcolor="white", gridwidth=1, griddash="solid",
                #showspikes=True,
                mirror=True,
                ticklabelstandoff=0,
                tickformat=",",
                overlaying='y',
                )
            )
    return fig
#display(disp_Corr_Lisk_Return_Asset_click("TOPIX","日経平均"))
#display(disp_Corr_Lisk_Return_Asset_click("ゆうちょ銀⾏(SBI証券)","日経平均"))
def disp_Corr_Lisk_Return_Asset_click2(asset):
    fig = go.Figure()
    df = cAnsys.cal_Corr_Asset_Asset()
    if asset in df:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[asset],
                mode="markers",
                customdata = df.index,
                hovertemplate =
                    '<br><i>銘柄</i>:¥%{x}'+
                    '<br><i>相関係数</i>:%{y:.2}<extra></extra>',
                marker=dict(
                    size = 12,
                    color = df[asset],
                    colorscale = "BlueRed",
                    cmid=0,
                    ),
                visible=True,
                )
            )      
        fig.update_xaxes(
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            mirror=True,
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            ticklabelstandoff=0,
            gridcolor="white", gridwidth=1, griddash="solid",
            showticklabels =False
            )
        fig.update_yaxes(
            title="Corr",
            title_standoff=5,
            fixedrange=False,
            tickfont=dict(size=10, color=dSet.ConstALL_axis_tick_color),
            title_font_color = dSet.ConstALL_axis_tick_color,
            title_font_size = 10,
            gridcolor="white", gridwidth=1, griddash="solid",
            showspikes=True,
            mirror=True,
            ticklabelstandoff=0,
            range=(-1,1)
            )
        fig.update_layout(
            title = dict(
                text = asset,
                font = dict(size = 14, color = dSet.ConstALL_title_color),
                xref = 'container',
                yref = "container",
                x = 0.5, y =0.98,
                xanchor = 'center',
                yanchor = 'top'
                ),
            width=None,
            height=None,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor=dSet.ConstALL_bgcolor,
            plot_bgcolor=dSet.ConstALL_bgcolor,
            showlegend = False,
            autosize=True,
            )
    return fig
#display(disp_Corr_Lisk_Return_Asset_click2("ゆうちょ銀⾏(SBI証券)"))
##################################################################################
