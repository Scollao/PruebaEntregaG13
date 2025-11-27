import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
import numpy as np
import base64
import json


# Load data
df = pd.read_csv("team_data_pop.csv")
df['TV_Homes'] = df['TV_Homes'].astype(float)
df['Population'] = df['Population'].astype(float)

df.sort_values(by='Chmp', ascending=True, inplace=True)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df['Chmp'],
    y=df['Tm'],
    #mode='markers',
    text = df['Chmp'].astype(str),
    textposition='outside',
    hovertext=df['Tm'],
    hoverinfo='text',
    orientation='h',
    marker=dict(
        color='mediumseagreen',
        line=dict(
            color='seagreen',
            width=2)

    
)))

logo_path = Path("NFL_Logos")  
min_logo = 0.1
max_logo = 0.3

# Scale win loss percentage

# Exaggerate differences by raising to a power (>1)
exp_factor = 2.5  # tweak between 2–3 for more exaggeration

for idx, row in df.iterrows():
    png_file = logo_path / f"{row['Tm'].lower().replace(' ', '')}.png"  
    if png_file.exists():
            normalized = (row["W-L%.1"] - df["W-L%.1"].min()) / (df["W-L%.1"].max() - df["W-L%.1"].min())
            scale = min_logo + (normalized ** exp_factor) * (max_logo - min_logo)
            fig.add_layout_image(
                x= -0.5 ,
                y=row['Tm'],
                source=Image.open(png_file),
                xref="x",
                yref="y",
                sizex= 1.3,
                sizey= 1.3,
                xanchor="center",
                yanchor="middle",
            )

fig.update_layout(
    clickmode='event+select',   # permite seleccionar en hover/click
    hovermode='closest'
)
fig.update_layout(
   title={
       'text': "NFL Teams: Championships Won",
       'x': 0.5,
       'xanchor': 'center',
       'font': {'size': 16}
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
       showticklabels=True,
       showline=True,
       linewidth=2,
       linecolor='black'
   ),
   width=1400,
   height=900,
   margin=dict(l=80, r=50, t=120, b=80)
)

# --- Extract last word from team name for video ---
df['VideoKey'] = df['Tm'].apply(lambda x: x.split()[-1])

# --- Load video paths instead of embedding (much smaller HTML) ---
video_path = Path("Videos")
team_videos = {}
for _, row in df.iterrows():
    video_file = video_path / f"{row['VideoKey']}.mp4"
    if video_file.exists():
        # Store the relative path for direct loading
        team_videos[row['Tm']] = f"Videos/{row['VideoKey']}.mp4"
    else:
        team_videos[row['Tm']] = None


plotly_html = fig.to_html(config={'staticPlot': False}, include_plotlyjs=True)

container_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <style>
        body {{
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f5f5f5;
            font-family: Arial, sans-serif;
        }}
        .chart-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            max-width: 100%;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        {plotly_html}
        <audio id = "CrowdAudio" controls>
            <source src="Audio/CheeringSFX.mp3" type="audio/mpeg">
        </audio>
    </div>

    <script>
    document.addEventListener("DOMContentLoaded", function() {{
         
        var audio = document.getElementById("CrowdAudio");
        var graphDiv = document.querySelector(".plotly-graph-div");

        var teamWins = {json.dumps(dict(zip(df['Tm'], df['Chmp'])))};

        graphDiv.on('plotly_click', function(data) {{

            if (!data.points.length) return;

            var team = data.points[0].y;  
            var wins = teamWins[team];

            var maxWins = Math.max(...Object.values(teamWins));
            var volume = wins / maxWins;

            volume = Math.max(0.1, volume);
            volume = Math.min(1.0, volume);

            audio.volume = volume;
            audio.currentTime = 0;
            audio.play();
        }});
    }});
    </script>
</body>
</html>"""

with open("NFL_Teams_Chart4.html", "w", encoding="utf-8") as f:
    f.write(container_html)
