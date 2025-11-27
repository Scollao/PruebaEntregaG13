import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from PIL import Image
import base64
import json

# --- Load data ---
df = pd.read_csv("team_data_pop.csv")
df['TV_Homes'] = df['TV_Homes'].astype(float)
df['Chmp'] = df['Chmp'].astype(float)
df['Founded'] = df.get('Founded', pd.Series([1970]*len(df)))
df['W-L%.1'] = df['W-L%.1'].astype(float)

# Sample blurbs
sample_blurbs = [
    "Historic franchise with multiple championships.",
    "Strong defense and passionate fan base.",
    "Recent playoff contender with young talent.",
    "Emerging powerhouse with large TV market.",
    "Classic rivalry team with rich legacy."
]
df['Blurb'] = [sample_blurbs[i % len(sample_blurbs)] for i in range(len(df))]

# --- Prepare figure ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['TV_Homes'],
    y=df['Chmp'],
    mode='markers+text',
    marker=dict(size=30),
    text=df['Tm'],
    textposition='top center',
    hoverinfo='text'
))

# Add logos
logo_path = Path("NFL_Logos")
default_logo_scale = 0.1
for _, row in df.iterrows():
    png_file = logo_path / f"{row['Tm'].lower().replace(' ', '')}.png"
    if png_file.exists():
        fig.add_layout_image(
            x=row['TV_Homes'],
            y=row['Chmp'],
            source=Image.open(png_file),
            xref="x",
            yref="y",
            sizex=default_logo_scale * df['TV_Homes'].max(),
            sizey=default_logo_scale * df['Chmp'].max(),
            xanchor="center",
            yanchor="middle",
        )

fig.update_layout(
    title="NFL Teams: Market Size vs Championships",
    xaxis_title="TV Market Size (Millions)",
    yaxis_title="Championships Won",
    width=1200,
    height=700,
    margin=dict(l=80, r=80, t=80, b=80)
)

# --- Load video ---
video_file = "Videos/test_video.mp4"
with open(video_file, "rb") as f:
    video_base64 = base64.b64encode(f.read()).decode("utf-8")

# Use 'From' column for founding year
df['From'] = df.get('From', pd.Series([1970]*len(df)))

team_data_json = json.dumps({
    row["Tm"]: {
        "blurb": row["Blurb"],
        "winrate": float(row["W-L%.1"]),
        "founded": int(row["From"])
    }
    for _, row in df.iterrows()
})

custom_html = f"""
<style>
#right-line, #bottom-line {{
    position: fixed;
    background-color: gray;
}}
#right-line {{
    top: 80px;
    right: 60px;
    width: 2px;
    height: 400px;
}}
#bottom-line {{
    left: 80px;
    bottom: 60px;
    width: 400px;
    height: 2px;
}}
.indicator-dot {{
    position: fixed;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: red;
    display: none;
}}
.indicator-label {{
    position: fixed;
    font-family: sans-serif;
    font-size: 14px;
    color: black;
    display: none;
}}
#hoverVideo {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 320px;
    border-radius: 10px;
    display: none;
}}
#hoverCaption {{
    position: fixed;
    bottom: 10px;
    right: 20px;
    width: 320px;
    background: rgba(0,0,0,0.7);
    color: white;
    font-family: sans-serif;
    font-size: 14px;
    padding: 8px;
    border-radius: 0 0 10px 10px;
    display: none;
    text-align: center;
}}
</style>

<div id="right-line"></div>
<div id="bottom-line"></div>
<div id="right-dot" class="indicator-dot"></div>
<div id="bottom-dot" class="indicator-dot"></div>
<div id="right-label" class="indicator-label"></div>
<div id="bottom-label" class="indicator-label"></div>

<video id="hoverVideo" muted loop>
    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
</video>
<div id="hoverCaption"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
    const teamData = {team_data_json};

    const minWin = Math.min(...Object.values(teamData).map(t => t.winrate));
    const maxWin = Math.max(...Object.values(teamData).map(t => t.winrate));
    const minYear = Math.min(...Object.values(teamData).map(t => t.founded));
    const maxYear = Math.max(...Object.values(teamData).map(t => t.founded));

    const video = document.getElementById('hoverVideo');
    const caption = document.getElementById('hoverCaption');

    const rightDot = document.getElementById('right-dot');
    const bottomDot = document.getElementById('bottom-dot');
    const rightLabel = document.getElementById('right-label');
    const bottomLabel = document.getElementById('bottom-label');

    const rightLine = document.getElementById('right-line');
    const bottomLine = document.getElementById('bottom-line');

    const plot = document.querySelector('.plotly');
    let currentTeam = null;

    plot.addEventListener('mousemove', (e) => {{
        const hover = document.querySelector('.hoverlayer .hovertext');
        if(hover){{
            const teamName = hover.textContent.trim();
            const team = teamData[teamName];
            if(team && teamName !== currentTeam){{
                currentTeam = teamName;
                caption.textContent = team.blurb;

                // --- Position right dot (Win %) ---
                const winNorm = (team.winrate - minWin)/(maxWin - minWin);
                const rightTop = rightLine.getBoundingClientRect().top;
                const rightHeight = rightLine.offsetHeight;
                rightDot.style.top = rightTop + rightHeight - winNorm*rightHeight - rightDot.offsetHeight/2 + 'px';
                rightDot.style.left = rightLine.getBoundingClientRect().left - rightDot.offsetWidth/2 + 'px';
                rightDot.style.display = 'block';

                rightLabel.style.top = rightTop + rightHeight - winNorm*rightHeight - rightLabel.offsetHeight/2 + 'px';
                rightLabel.style.left = rightLine.getBoundingClientRect().left + 15 + 'px';
                rightLabel.textContent = team.winrate;
                rightLabel.style.display = 'block';

                // --- Position bottom dot (Founded Year) ---
                const yearNorm = (team.founded - minYear)/(maxYear - minYear);
                const bottomLeft = bottomLine.getBoundingClientRect().left;
                const bottomWidth = bottomLine.offsetWidth;
                bottomDot.style.left = bottomLeft + yearNorm*bottomWidth - bottomDot.offsetWidth/2 + 'px';
                bottomDot.style.top = bottomLine.getBoundingClientRect().top - bottomDot.offsetHeight/2 + 'px';
                bottomDot.style.display = 'block';

                bottomLabel.style.left = bottomLeft + yearNorm*bottomWidth - bottomLabel.offsetWidth/2 + 'px';
                bottomLabel.style.top = bottomLine.getBoundingClientRect().top - bottomLabel.offsetHeight - 5 + 'px';
                bottomLabel.textContent = team.founded;
                bottomLabel.style.display = 'block';

                // --- Show video and caption ---
                video.style.display='block';
                caption.style.display='block';
                video.pause(); video.currentTime=0; video.play();
            }}
        }} else {{
            currentTeam = null;
            video.style.display='none';
            caption.style.display='none';
            rightDot.style.display='none';
            bottomDot.style.display='none';
            rightLabel.style.display='none';
            bottomLabel.style.display='none';
        }}
    }});
}});
</script>
"""



# --- Export ---
html_out = fig.to_html(include_plotlyjs=True, full_html=False)
final_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
{html_out}
{custom_html}
</body>
</html>
"""

with open("NFL_Hover_Interactive.html", "w", encoding="utf-8") as f:
    f.write(final_html)

