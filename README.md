# TerpBites

Project site for INST362 Group 25. Plain HTML, CSS, and JavaScript. No build step.

## Files

- `index.html`, `styles.css`, `script.js`: the site
- `data/dining.js`: real UMD dining data the site reads (generated, don't edit by hand)
- `scripts/update_data.py`: rebuilds `data/dining.js`

## Refreshing the dining data

The site shows hours for about three weeks and dining hall menus for three days from the last time the data was pulled. To refresh:

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
