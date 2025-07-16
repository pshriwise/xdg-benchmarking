# GitHub Pages Setup Guide

This guide will help you host the XDG Benchmarking Dashboard on GitHub Pages.

## Overview

GitHub Pages only serves static files (HTML, CSS, JS), so we've created a static version of the dashboard that generates HTML files from your benchmark data.

## Step 1: Generate Static Dashboard

Run the static dashboard generator to create the HTML files:

```bash
python static_dashboard.py
```

This will:
- Load all your benchmark data from `results/`
- Generate interactive charts using Plotly
- Create a complete HTML dashboard in `docs/index.html`
- Copy all assets (CSS, logo) to the `docs/` folder

## Step 2: Push to GitHub

1. **Create a new repository** on GitHub (or use existing)
2. **Push your code** to GitHub:

```bash
git add .
git commit -m "Add static dashboard for GitHub Pages"
git push origin master
```

## Step 3: Enable GitHub Pages

1. Go to your GitHub repository
2. Click **Settings** tab
3. Scroll down to **Pages** section
4. Under **Source**, select **Deploy from a branch**
5. Choose **main** (or **master**) branch
6. Select **/docs** folder
7. Click **Save**

## Step 4: Access Your Dashboard

Your dashboard will be available at:
```
https://[your-username].github.io/[repository-name]/
```

## Updating the Dashboard

When you add new benchmark data:

1. **Generate new static files**:
   ```bash
   python static_dashboard.py
   ```

2. **Commit and push**:
   ```bash
   git add docs/
   git commit -m "Update dashboard with new data"
   git push origin master
   ```

3. **GitHub Pages will automatically update** (may take a few minutes)

## Features of the Static Dashboard

✅ **Interactive Charts**: All charts are fully interactive using Plotly
✅ **Responsive Design**: Works on desktop and mobile
✅ **XDG Branding**: Includes your logo and styling
✅ **Complete Data**: Shows all your benchmark results
✅ **No Server Required**: Runs entirely in the browser

## File Structure

```
your-repo/
├── dashboard.py          # Interactive Dash app (for local use)
├── static_dashboard.py   # Static HTML generator
├── assets/
│   ├── dashboard.css     # Styling
│   └── xdg-logo.png     # Logo
├── docs/                 # GitHub Pages folder
│   ├── index.html       # Generated dashboard
│   └── assets/          # Copied assets
├── results/             # Your benchmark data
└── README.md
```

## Troubleshooting

### Charts Not Loading
- Check that Plotly.js is loading (check browser console)
- Ensure your data files are valid JSON

### Styling Issues
- Verify `assets/dashboard.css` was copied to `docs/assets/`
- Check that the logo file exists in `docs/assets/`

### Data Not Showing
- Run `python static_dashboard.py` to regenerate
- Check that your `results/` folder contains valid data
- Verify JSON files follow the expected schema

## Alternative: GitHub Actions (Advanced)

For automatic updates, you can set up a GitHub Action:

```yaml
# .github/workflows/update-dashboard.yml
name: Update Dashboard
on:
  push:
    paths:
      - 'results/**'
  workflow_dispatch:

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install pandas plotly
      - run: python static_dashboard.py
      - run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "Auto-update dashboard" || exit 0
          git push
```

This will automatically regenerate and deploy the dashboard whenever you add new benchmark data!

## Support

If you encounter issues:
1. Check the browser console for errors
2. Verify your data format matches the schema
3. Ensure all files are properly committed to GitHub
4. Check GitHub Pages settings and deployment status