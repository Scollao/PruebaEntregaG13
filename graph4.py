import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
import numpy as np

# Load data
df = pd.read_csv("team_data_pop.csv")
df['TV_Homes'] = df['TV_Homes'].astype(float)
df['Population'] = df['Population'].astype(float)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['TV_Homes'],
    y=df['Chmp'],
    mode='markers',
    marker=dict(size=0.5),
    hovertext=df['Tm'],
    hoverinfo='text'
))

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
                x=row['TV_Homes'],
                y=row['Chmp'],
                source=Image.open(png_file),
                xref="x",
                yref="y",
                sizex=scale * df['TV_Homes'].max(),
                sizey=scale * df['Chmp'].max(),
                xanchor="center",
                yanchor="middle",
            )

fig.update_layout(
   title={
       'text': "NFL Teams: TV Market Size vs Championships Won<br><sub>Note: Logo size is proportional to Winning Percentage</sub>",
       'x': 0.5,
       'xanchor': 'center',
       'font': {'size': 16}
   },
   xaxis_title="TV Market Size (Millions of TV Households)",
   yaxis_title="Championships Won",
   xaxis=dict(
       showgrid=True,
       range=[0, df['TV_Homes'].max() * 1.1],
       showline=True,
       linewidth=2,
       linecolor='black'
   ),
   yaxis=dict(
       showgrid=True,
       range=[-0.5, df['Chmp'].max() + 1],
       showline=True,
       linewidth=2,
       linecolor='black'
   ),
   width=1400,
   height=900,
   margin=dict(l=80, r=50, t=120, b=80)
)

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
    </div>
</body>
</html>"""

with open("NFL_Teams_Chart.html", "w", encoding="utf-8") as f:
    f.write(container_html)
