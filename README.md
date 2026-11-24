# Syria Trek

Source lives in `src/`. GitHub Pages serves `docs/`, which is generated:

    pip install pillow minify-html
    python3 build.py

The build converts every photo to responsive WebP with content-hashed
filenames (so a replaced photo always gets a fresh URL and never shows a
stale cached copy), preloads the hero image, and minifies the page into a
single index.html. `img/preview.jpg` keeps its fixed name for link previews.
