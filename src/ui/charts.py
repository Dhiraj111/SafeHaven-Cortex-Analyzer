import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_map(df_geo):
    df_geo['REGION'] = df_geo['REGION'].str.lower()
    region_map = {'southeast': 'GA', 'northeast': 'NY', 'west': 'CA', 'southwest': 'TX', 'northwest': 'WA', 'midwest': 'IL'}
    df_geo['STATE'] = df_geo['REGION'].apply(lambda x: region_map.get(x, 'CA')) 
    
    fig = px.choropleth(df_geo, locations='STATE', locationmode="USA-states", 
                        color='AVG_COST', scope="usa", color_continuous_scale="Reds", 
                        title="Avg Medical Cost by Region")
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def render_stress_chart(probs):
    fig = px.area(x=["-20%", "Base", "+20%", "+40%", "+60%"], y=probs, color_discrete_sequence=['#E74C3C'])
    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Cost Volatility", yaxis_title="Risk Prob %")
    return fig

def render_correlation(df_agg, threshold):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df_agg['CREDIT_GRADE'], y=df_agg['TOTAL_CUSTOMERS'], name="Volume", marker_color='#2E86C1'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_agg['CREDIT_GRADE'], y=df_agg['COST_TO_INCOME_RATIO'], name="Risk %", line=dict(color='#E74C3C', width=3)), secondary_y=True)
    fig.add_hrect(y0=threshold, y1=threshold+0.5, line_width=0, fillcolor="red", opacity=0.3)
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=0), legend=dict(orientation="h", y=1.2))
    return fig