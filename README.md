# TerpBites

Project site for INST362 Group 25. Plain HTML, CSS, and JavaScript. No build step.

## Files

- `index.html`, `styles.css`, `script.js`: the site
- `data/dining.js`: real UMD dining data the site reads (generated, don't edit by hand)
- `scripts/update_data.py`: rebuilds `data/dining.js`

## Refreshing the dining data

A GitHub Action (`.github/workflows/deploy.yml`) pulls fresh data and redeploys the site every morning at about 5 AM Eastern, and on every push to `main`. To run it right away, go to the repo's **Actions** tab, choose **Refresh dining data and deploy**, and click **Run workflow**.

GitHub pauses scheduled workflows after 60 days with no commits. If that happens, re-enable the workflow from the Actions tab.

To refresh the local copy for previewing:

```bash
python3 scripts/update_data.py
```

It needs Python 3.9+ and no extra packages. It pulls from:

- **Hours**: the public Google Sheet that dining.umd.edu reads its hours from
- **Menus**: nutrition.umd.edu (South Campus, Yahentamitsi, 251 North)
- **Building locations**: api.umd.io, used to estimate walk times

## Previewing

Open `index.html` in a browser, or run a local server:

```bash
python3 -m http.server 8362
```

## Editing the findings report

The Research Findings and Analysis report builds itself from three files in `report/`:

- `content.md`: all the text. Edit it on GitHub (open the file, click the pencil, then **Commit changes**). The notes at the top of the file explain the formatting.
- `data.json`: the numbers, titles, and captions for the charts and stat boxes.
- `style.css` and `build.py`: the look and the build step. You shouldn't need to touch these.

After each commit, the GitHub Action rebuilds the report. A few minutes later the new version is at:

- PDF: https://arjunbojja1.github.io/TerpBites/report/TerpBites_Findings.pdf
- Web version: https://arjunbojja1.github.io/TerpBites/report/findings.html

To build it on your own computer: `pip install markdown`, then `python3 report/build.py`, and open `report/findings.html`.
