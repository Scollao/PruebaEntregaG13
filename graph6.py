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
df['W-L%.1'] = df['W-L%.1'].astype(float)

print(df)

# --- Extract last word from team name for video ---
df['VideoKey'] = df['Tm'].apply(lambda x: x.split()[-1])

# --- Prepare figure ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['Tm'],
    y=df['Chmp'],
    #mode='markers',
   marker=dict(size=30),
   text=df['Tm'],
   hoverinfo='text',

))

#fig.add_trace(go.Bar(
#    x=df['Tm'],
#    y=df['Chmp'],
#    text=df['Tm'],
#    hoverinfo='text',
#    ))

# Add logos
logo_path = Path("NFL_Logos")
default_logo_scale = 0.1
for _, row in df.iterrows():
    png_file = logo_path / f"{row['Tm'].lower().replace(' ', '')}.png"
    if png_file.exists():
        fig.add_layout_image(
            x=row['Tm'],
            y=row['Chmp'],
            source=Image.open(png_file),
            xref="x",
            yref="y",
            sizex=0.8,
            sizey=0.8,
            xanchor="center",
            yanchor="middle",
        )

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



# --- Prepare JSON for JS ---
team_data_json = json.dumps({
    row["Tm"]: {
        "winrate": float(row["W-L%.1"]),
        "founded": int(row["From"]),
        "video": team_videos[row["Tm"]],
        "tv_homes": float(row["TV_Homes"]),
        "championships": float(row["Chmp"])
    }
    for _, row in df.iterrows()
})

# --- Custom HTML/JS ---
custom_html = f"""
<style>
body {{
    margin: 0;
    padding: 20px;
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}}

.container {{
    max-width: 1200px;
    width: 100%;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    padding: 30px 100px 60px 30px;
    position: relative;
    transform-origin: center;
}}

#right-line, #bottom-line {{
    position: absolute;
    background-color: gray;
    pointer-events: none;
    z-index: 1000;
}}
#right-line {{
    width: 2px;
    height: 0px;
}}
#bottom-line {{
    width: 0px;
    height: 2px;
}}
.indicator-dot {{
    position: fixed;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: red;
    display: none;
    z-index: 1000;
}}
.indicator-label {{
    position: fixed;
    font-family: sans-serif;
    font-size: 14px;
    color: black;
    display: none;
    z-index: 999999 !important;
    background: white;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}
.connecting-line {{
    position: fixed;
    background-color: rgba(255, 0, 0, 0.6);
    height: 2px;
    display: none;
    pointer-events: none;
    z-index: 1000;
}}
.axis-label {{
    position: absolute;
    font-family: sans-serif;
    font-size: 12px;
    color: #666;
    pointer-events: none;
    z-index: 99999 !important;
    background: white;
    padding: 2px 4px;
    border-radius: 3px;
    border: 1px solid #ddd;
    transform-origin: center;
}}

/* Ensure all interactive elements scale with the container */
.container * {{
    transform-origin: center;
}}

/* Make sure the plotly container scales properly */
.plotly {{
    transform-origin: center;
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

.axis-title {{
    position: absolute;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;       /* bigger than tick labels */
    font-weight: 700;       /* bold */
    color: #111;            /* darker text */
    background: #fff;
    padding: 6px 10px;
    border-radius: 6px;
    border: 2px solid #555;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    z-index: 100001 !important;
    pointer-events: none;
}}


</style>

<div id="right-line"></div>
<div id="bottom-line"></div>
<div id="right-dot" class="indicator-dot"></div>
<div id="bottom-dot" class="indicator-dot"></div>
<div id="right-label" class="indicator-label"></div>
<div id="bottom-label" class="indicator-label"></div>
<div id="line-to-right" class="connecting-line"></div>
<div id="line-to-bottom" class="connecting-line"></div>
<div id="line-to-right-label" class="axis-title">Win %</div>
<div id="line-to-bottom-label" class="axis-title">Founded Year</div>

<!-- Axis labels containers -->
<div id="right-axis-labels"></div>
<div id="bottom-axis-labels"></div>


<video id="hoverVideo" loop>
    <source src="" type="video/mp4">
</video>
<div id="hoverCaption"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
    const teamData = {team_data_json};

    const minWin = Math.min(...Object.values(teamData).map(t => t.winrate));
    const maxWin = Math.max(...Object.values(teamData).map(t => t.winrate));
    const minYear = Math.min(...Object.values(teamData).map(t => t.founded));
    const maxYear = Math.max(...Object.values(teamData).map(t => t.founded));
    
    // Get plot data ranges for coordinate conversion
    const minTV = Math.min(...Object.values(teamData).map(t => t.tv_homes));
    const maxTV = Math.max(...Object.values(teamData).map(t => t.tv_homes));
    const minChmp = Math.min(...Object.values(teamData).map(t => t.championships));
    const maxChmp = Math.max(...Object.values(teamData).map(t => t.championships));

    const video = document.getElementById('hoverVideo');
    const caption = document.getElementById('hoverCaption');

    const rightDot = document.getElementById('right-dot');
    const bottomDot = document.getElementById('bottom-dot');
    const rightLabel = document.getElementById('right-label');
    const bottomLabel = document.getElementById('bottom-label');

    const rightLine = document.getElementById('right-line');
    const bottomLine = document.getElementById('bottom-line');
    
    const lineToRight = document.getElementById('line-to-right');
    const lineToBottom = document.getElementById('line-to-bottom');
    
    const rightAxisLabels = document.getElementById('right-axis-labels');
    const bottomAxisLabels = document.getElementById('bottom-axis-labels');

    const plot = document.querySelector('.plotly');
    let currentTeam = null;

    // Function to update reference lines based on plot bounds
    function updateReferenceLines() {{
        // Get the main plotly container
        const plotlyContainer = document.querySelector('.plotly');
        if (!plotlyContainer) return;
        
        // Get the container for relative positioning
        const container = document.querySelector('.container');
        if (!container) return;
        
        // Get the SVG element which contains the actual plot area
        const svg = plotlyContainer.querySelector('svg');
        if (!svg) return;
        
        // Find the actual plot area by looking for the main plot group
        const plotArea = svg.querySelector('.plotly .main-svg .plotly .plot');
        if (!plotArea) {{
            // Fallback: try to find the main plot group
            const mainPlot = svg.querySelector('.plotly .plot');
            if (mainPlot) {{
                const plotRect = mainPlot.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                const relativeRect = {{
                    left: plotRect.left - containerRect.left,
                    right: plotRect.right - containerRect.left,
                    top: plotRect.top - containerRect.top,
                    bottom: plotRect.bottom - containerRect.top,
                    width: plotRect.width,
                    height: plotRect.height
                }};
                positionLines(relativeRect);
                createAxisLabels(relativeRect);

                return;
            }}
            
        }}
        
        if (plotArea) {{
            const plotRect = plotArea.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            const relativeRect = {{
                left: plotRect.left - containerRect.left,
                right: plotRect.right - containerRect.left,
                top: plotRect.top - containerRect.top,
                bottom: plotRect.bottom - containerRect.top,
                width: plotRect.width,
                height: plotRect.height
            }};
            positionLines(relativeRect);
            createAxisLabels(relativeRect);
        }} else {{
            // Final fallback: use SVG with margins
            const svgRect = svg.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            const margin = 60; // Approximate margin
            const relativeRect = {{
                left: (svgRect.left - containerRect.left) + margin,
                right: (svgRect.right - containerRect.left) - margin,
                top: (svgRect.top - containerRect.top) + margin,
                bottom: (svgRect.bottom - containerRect.top) - margin,
                width: svgRect.width - 2 * margin,
                height: svgRect.height - 2 * margin
            }};
            positionLines(relativeRect);
            createAxisLabels(relativeRect);
        }}
    }}
    
    // Function to position the reference lines
    function positionLines(plotRect) {{
        const offset = 80; // Distance from the plot area

        const container = document.querySelector('.container');
        const containerRect = container.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const containerHeight = containerRect.height;

        // --- Position right line ---
        const rightLineLeft = Math.min(plotRect.right + offset, containerWidth - 10);
        rightLine.style.left = rightLineLeft + 'px';
        rightLine.style.top = plotRect.top + 'px';
        rightLine.style.height = plotRect.height + 'px';

        // --- Position bottom line ---
        const bottomLineTop = Math.min(plotRect.bottom + offset, containerHeight - 10);
        bottomLine.style.left = plotRect.left + 'px';
        bottomLine.style.top = bottomLineTop + 'px';
        bottomLine.style.width = plotRect.width + 'px';

        // --- Position static axis labels ---
        const lineRightLabel = document.getElementById('line-to-right-label');
        const lineBottomLabel = document.getElementById('line-to-bottom-label');

        if (lineRightLabel && lineBottomLabel) {{
            // Right axis label: vertically centered along the right line
            lineRightLabel.style.left = (rightLineLeft + 5) + 'px'; // small spacing from the line
            lineRightLabel.style.top = (plotRect.top + plotRect.height / 2 - lineRightLabel.offsetHeight / 2) + 'px';
            lineRightLabel.style.display = 'block';

            // Bottom axis label: horizontally centered below the bottom line
            lineBottomLabel.style.left = (plotRect.left + plotRect.width / 2 - lineBottomLabel.offsetWidth / 2) + 'px';
            lineBottomLabel.style.top = (bottomLineTop + 5) + 'px'; // small spacing below the line
            lineBottomLabel.style.transform = 'rotate(0deg)';
            lineBottomLabel.style.display = 'block';
        }}
    }}

    
    // Function to create numerical labels along the axes
    function createAxisLabels(plotRect) {{
        // Clear existing labels
        rightAxisLabels.innerHTML = '';
        bottomAxisLabels.innerHTML = '';
        
        // Get container bounds for safe positioning
        const container = document.querySelector('.container');
        const containerRect = container.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const containerHeight = containerRect.height;
        const offset = 80;
        
        // Create labels for right axis (Win %)
        const winSteps = 5; // Number of steps from min to max
        for (let i = 0; i <= winSteps; i++) {{
            const winValue = minWin + (maxWin - minWin) * (i / winSteps);
            const label = document.createElement('div');
            label.className = 'axis-label';
            label.textContent = (winValue * 100).toFixed(1) + '%';
            
            // Position along the right line with boundary checking
            const yPos = plotRect.top + (plotRect.height * (winSteps - i) / winSteps);
            const rightLineLeft = Math.min(plotRect.right + offset, containerWidth - 10);
            label.style.left = (rightLineLeft + 5) + 'px'; // 5px spacing from line
            label.style.top = (yPos - 8) + 'px';
            
            rightAxisLabels.appendChild(label);
        }}
        
        // Create labels for bottom axis (Founded Year) - every 10 years
        const startYear = Math.ceil(minYear / 10) * 10; // Round up to nearest 10
        const endYear = Math.floor(maxYear / 10) * 10;   // Round down to nearest 10
        
        for (let year = startYear; year <= endYear; year += 10) {{
            // Only show if within the actual data range
            if (year >= minYear && year <= maxYear) {{
                const label = document.createElement('div');
                label.className = 'axis-label';
                label.textContent = year.toString();
                
                // Calculate position based on the year's position in the range
                const yearPosition = (year - minYear) / (maxYear - minYear);
                const xPos = plotRect.left + (plotRect.width * yearPosition);
                const bottomLineTop = Math.min(plotRect.bottom + offset, containerHeight - 10);
                label.style.left = (xPos - 15) + 'px';
                label.style.top = (bottomLineTop - 25) + 'px'; // 25px above the line (consistent with dynamic labels)
                
                bottomAxisLabels.appendChild(label);
            }}
        }}
    }}

    // Update lines when plot is ready, resized, zoomed, or panned
    plot.addEventListener('plotly_afterplot', updateReferenceLines);
    plot.addEventListener('plotly_relayout', updateReferenceLines);
    plot.addEventListener('plotly_redraw', updateReferenceLines);
    window.addEventListener('resize', updateReferenceLines);
    
    // Initial positioning with multiple attempts to ensure proper setup
    setTimeout(updateReferenceLines, 100);
    setTimeout(updateReferenceLines, 500);
    setTimeout(updateReferenceLines, 1000);

    plot.addEventListener('mousemove', (e) => {{
        const hover = document.querySelector('.hoverlayer .hovertext');
        if(hover){{
            const teamName = hover.textContent.trim();
            const team = teamData[teamName];
            if(team && teamName !== currentTeam){{
                currentTeam = teamName;
                caption.textContent = "Video de campeonato más reciente";
                
                // Small delay to ensure line dimensions are calculated
                setTimeout(() => {{

                // --- Position right dot (Win %) ---
                const winNorm = (team.winrate - minWin)/(maxWin - minWin);
                const rightLineRect = rightLine.getBoundingClientRect();
                const rightTop = rightLineRect.top;
                const rightHeight = rightLineRect.height;
                // For a vertical line, the center is at the left edge + half the line width
                const rightCenter = rightLineRect.left + (rightLineRect.width / 2);
                rightDot.style.top = rightTop + rightHeight - winNorm*rightHeight - rightDot.offsetHeight/2 + 'px';
                rightDot.style.left = rightCenter - rightDot.offsetWidth/2 + 'px'; // Center on the line
                rightDot.style.display = 'block';
                
                // Ensure dot is perfectly centered with a small adjustment
                const dotLeft = rightCenter - rightDot.offsetWidth/2;
                rightDot.style.left = dotLeft + 'px';

                rightLabel.style.top = rightTop + rightHeight - winNorm*rightHeight - rightLabel.offsetHeight/2 + 'px';
                rightLabel.style.left = rightLineRect.left + 15 + 'px';
                rightLabel.textContent = (team.winrate * 100).toFixed(1) + '%';
                rightLabel.style.display = 'block';

                // --- Position bottom dot (Founded Year) ---
                const yearNorm = (team.founded - minYear)/(maxYear - minYear);
                const bottomLineRect = bottomLine.getBoundingClientRect();
                const bottomLeft = bottomLineRect.left;
                const bottomWidth = bottomLineRect.width;
                // For a horizontal line, the center is at the top edge + half the line height
                const bottomCenter = bottomLineRect.top + (bottomLineRect.height / 2);
                bottomDot.style.left = bottomLeft + yearNorm*bottomWidth - bottomDot.offsetWidth/2 + 'px';
                bottomDot.style.top = bottomCenter - bottomDot.offsetHeight/2 + 'px'; // Center on the line
                bottomDot.style.display = 'block';
                
                // Ensure dot is perfectly centered with a small adjustment
                const dotTop = bottomCenter - bottomDot.offsetHeight/2;
                bottomDot.style.top = dotTop + 'px';

                // Position year label at consistent height above the red dot
                bottomLabel.style.left = bottomLeft + yearNorm*bottomWidth - bottomLabel.offsetWidth/2 + 'px';
                bottomLabel.style.top = (dotTop - 25) + 'px'; // Always 25px above the red dot
                bottomLabel.textContent = team.founded;
                bottomLabel.style.display = 'block';

                // --- Create connecting lines ---
                // Find all scatter plot points and get the one being hovered
                const scatterPoints = plot.querySelectorAll('.scatterlayer .point');
                let logoX = e.clientX;
                let logoY = e.clientY;
                
                // Try to find the exact point element being hovered
                scatterPoints.forEach(point => {{
                    const rect = point.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    
                    // Check if this point is close to our hover position
                    const distance = Math.sqrt(Math.pow(centerX - e.clientX, 2) + Math.pow(centerY - e.clientY, 2));
                    if (distance < 50) {{ // Within 50 pixels
                        logoX = centerX;
                        logoY = centerY;
                    }}
                }});
                
                // Line to right dot (winning percentage)
                const rightDotX = rightDot.getBoundingClientRect().left + rightDot.offsetWidth/2;
                const rightDotY = rightDot.getBoundingClientRect().top + rightDot.offsetHeight/2;
                
                const rightLineLength = Math.sqrt(Math.pow(rightDotX - logoX, 2) + Math.pow(rightDotY - logoY, 2));
                const rightLineAngle = Math.atan2(rightDotY - logoY, rightDotX - logoX) * 180 / Math.PI;
                
                lineToRight.style.left = logoX + 'px';
                lineToRight.style.top = logoY + 'px';
                lineToRight.style.width = rightLineLength + 'px';
                lineToRight.style.transform = `rotate(${{rightLineAngle}}deg)`;
                lineToRight.style.transformOrigin = '0 0';
                lineToRight.style.display = 'block';
                
                // Line to bottom dot (founded year)
                const bottomDotX = bottomDot.getBoundingClientRect().left + bottomDot.offsetWidth/2;
                const bottomDotY = bottomDot.getBoundingClientRect().top + bottomDot.offsetHeight/2;
                
                const bottomLineLength = Math.sqrt(Math.pow(bottomDotX - logoX, 2) + Math.pow(bottomDotY - logoY, 2));
                const bottomLineAngle = Math.atan2(bottomDotY - logoY, bottomDotX - logoX) * 180 / Math.PI;
                
                lineToBottom.style.left = logoX + 'px';
                lineToBottom.style.top = logoY + 'px';
                lineToBottom.style.width = bottomLineLength + 'px';
                lineToBottom.style.transform = `rotate(${{bottomLineAngle}}deg)`;
                lineToBottom.style.transformOrigin = '0 0';
                lineToBottom.style.display = 'block';

                // --- Show video and caption ---
                if(team.video){{
                    video.src = team.video;
                    video.load();
                    video.play();
                    const videoWidth = video.offsetWidth;
                    const offset = 20;

                    video.style.left = (e.clientX - 320 - offset) + 'px';
                    video.style.top = (e.clientY - 220 - offset) + 'px';
                    video.style.display = 'block'; // display first
                    setTimeout(() => {{
                        const videoRect = video.getBoundingClientRect();
                        caption.style.left = videoRect.left + 'px';
                        caption.style.top = (videoRect.bottom + 5) + 'px';
                        caption.style.display = 'block';
                    }}, 50);
                }}
                }}, 10); // End setTimeout
            }}
        }} else {{
            currentTeam = null;
            video.pause();
            video.currentTime=0;
            video.style.display='none';
            caption.style.display='none';
            rightDot.style.display='none';
            bottomDot.style.display='none';
            rightLabel.style.display='none';
            bottomLabel.style.display='none';
            lineToRight.style.display='none';
            lineToBottom.style.display='none';
        }}
    }});
}});
</script>
"""

fig.update_layout(
    width=1200, 
    height=800,
    title="NFL Teams: TV Market Size vs Championships Won",
    title_x=0.5,  # Center the title
    title_font_size=18,
    title_font_color="#333",
    xaxis_title="TV Market Size (Millions of TV Households)",
    yaxis_title="Championships Won",
    xaxis_title_font_size=14,
    yaxis_title_font_size=14,
    xaxis_title_font_color="#333",
    yaxis_title_font_color="#333"
)

# --- Export final HTML ---
html_out = fig.to_html(include_plotlyjs=True, full_html=False)
final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFL Teams: TV Market Size vs Championships Won</title>
</head>
<body>
    <div class="container">
        {html_out}
        {custom_html}
    </div>
</body>
</html>
"""

with open("NFL_Hover_Interactive.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("HTML with interactive hover videos generated!")
