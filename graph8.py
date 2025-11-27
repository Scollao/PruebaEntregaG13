import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
import json

# ================================
#   LOAD DATA
# ================================
df = pd.read_csv("team_data_pop.csv")

df['TV_Homes'] = df['TV_Homes'].astype(float)
df['Population'] = df['Population'].astype(float)
df['Chmp'] = df['Chmp'].astype(float)

df.sort_values(by='Chmp', ascending=True, inplace=True)

# ================================
#   BUILD PLOTLY FIGURE
# ================================
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['Chmp'],
    y=df['Tm'],
    text=df['Chmp'].astype(str),
    textposition='outside',
    hovertext=df['Tm'],
    hoverinfo='text',
    orientation='h',
    marker=dict(
        color='mediumseagreen',
        line=dict(color='seagreen', width=2)
    ),
    selected=dict(
        marker=dict(opacity=1)
    ),
    unselected=dict(
        marker=dict(opacity=0.2)
    )
))

# ================================
#   ADD TEAM LOGOS
# ================================
logo_path = Path("NFL_Logos")
min_logo = 0.1
max_logo = 0.3
exp_factor = 2.5  # exaggeration factor

for idx, row in df.iterrows():
    png_file = logo_path / f"{row['Tm'].lower().replace(' ', '')}.png"
    if png_file.exists():
        fig.add_layout_image(
            x=-0.5,
            y=row['Tm'],
            source=Image.open(png_file),
            xref="x",
            yref="y",
            sizex=1.3,
            sizey=1.3,
            xanchor="center",
            yanchor="middle",
        )

# ================================
#   STYLE
# ================================
fig.update_layout(
    title={
        'text': "NFL Teams: Championships Won",
        'x': 0.5,
        'font': {'size': 18}
    },
    xaxis_title="Championships Won",
    yaxis_title="Teams",
    xaxis=dict(
        showgrid=False,
        range=[-1.0, df['Chmp'].max() * 2],
        showline=True,
        linewidth=2,
        linecolor='black'
    ),
    yaxis=dict(
        showgrid=True,
        showline=True,
        linewidth=2,
        linecolor='black'
    ),
    width=1400,
    height=900,
    margin=dict(l=80, r=50, t=120, b=80),
    hovermode="closest"
)

# ================================
#   VIDEOS FOR EACH TEAM
# ================================
df['VideoKey'] = df['Tm'].apply(lambda x: x.split()[-1])

video_path = Path("Videos")
team_videos = {}

for _, row in df.iterrows():
    video_file = video_path / f"{row['VideoKey']}.mp4"
    if video_file.exists():
        team_videos[row['Tm']] = f"Videos/{row['VideoKey']}.mp4"
    else:
        team_videos[row['Tm']] = None

VIDEO_DICT_JSON = json.dumps(team_videos)

# ================================
#   GENERATE HTML
# ================================
plotly_html = fig.to_html(include_plotlyjs=True)

container_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
    body {{
        margin: 0;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        background-color: #f5f5f5;
        font-family: Arial, sans-serif;
    }}
    .chart-container {{
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

#hoverVideo {{
    position: fixed;
    width: 320px;
    border-radius: 10px;
    display: none;
    z-index: 10000;
}}
#hoverCaption {{
    position: fixed;
    background: rgba(0,0,0,0.7);
    color: white;
    font-family: sans-serif;
    font-size: 14px;
    padding: 8px;
    border-radius: 10px;
    text-align: center;
    z-index: 10001;
    display: none;
    width: 305px;
}}
</style>
</head>

<body>

<div class="chart-container">

    <!-- PLOTLY CHART -->
    {plotly_html}
    <audio controls>
        <source src="Audio/CheeringSFX.mp3" type="audio/mpeg">
    </audio>
</div>
    
<audio controls>
    <source src="Audio/CheeringSFX.mp3" type="audio/mpeg">
</audio>

</body>
</html>
"""

# ================================
#   SAVE HTML FILE
# ================================
with open("NFL_Teams_Chart3.html", "w", encoding="utf-8") as f:
    f.write(container_html)

print("Archivo generado: NFL_Teams_Chart.html")