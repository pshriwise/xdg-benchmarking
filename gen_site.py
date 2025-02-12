import plotly.express as px
from pathlib import Path
from jinja2 import Template

from scaling import model_html

# Ensure output directory exists
Path("dashboards").mkdir(exist_ok=True)


# Generate separate HTML files for each plot
print('Calling for Model HTML file generation...')
dashboard_files = model_html()

# Jinja2 template for index.html
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XDG Benchmarking</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            text-align: center;
        }
        h1 {
            color: #333;
            margin-top: 20px;
        }
        .container {
            width: 90%;
            max-width: 1000px;
            margin: auto;
            background: white;
            padding: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }
        .tab-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background: #ddd;
            border: 1px solid #ccc;
            border-bottom: none;
            margin-right: 5px;
            border-radius: 5px 5px 0 0;
        }
        .tab:hover {
            background: #bbb;
        }
        .active-tab {
            background: #fff;
            border-bottom: 2px solid white;
        }
        .sub-tab-container {
            display: none;
            margin-top: 10px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        iframe {
            width: 100%;
            height: 600px;
            border: none;
        }
    </style>
</head>
<body>

    <h1>XDG Benchmarking</h1>

    <div class="container">
        <!-- Main Category Tabs -->
        <div class="tab-container">
            {% for title, filename in dashboard_files.items() %}
                <div class="tab" onclick="openPlot(event, '{{ filename }}')">{{ title }}</div>
            {% endfor %}
        </div>

        <!-- Plot Content -->
        <div id="plot-container">
            <iframe id="plot-frame" src="" style="display: none;"></iframe>
        </div>
    </div>

    <script>
        function openCategory(event, categoryId) {
            // Hide all sub-tabs
            let subTabs = document.getElementsByClassName("sub-tab-container");
            for (let i = 0; i < subTabs.length; i++) {
                subTabs[i].style.display = "none";
            }

            // Show selected category's sub-tabs
            document.getElementById(categoryId).style.display = "block";
        }

        function openPlot(event, plotSrc) {
            let plotFrame = document.getElementById("plot-frame");
            plotFrame.src = plotSrc;
            plotFrame.style.display = "block";
        }
    </script>

</body>
</html>
"""

# Render the Jinja2 template with dynamic data
template = Template(html_template)
html_output = template.render(dashboard_files=dashboard_files)

# Save index.html
with open("index.html", "w") as f:
    f.write(html_output)

print("✅ Dynamic Dashboard with Categories & Tabs Generated!")
