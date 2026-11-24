# Syria Trek site

Teaser page for the HBS Syria Trek, 13–19 March 2027.
Live at https://rosesamarfarah.github.io/syriatrek/

## Layout

```
src/            editable source
  index.html    the page: HTML, CSS and JS in one file
  img/          original photos (full resolution JPEGs)
build.py        build script
docs/           generated site, served by GitHub Pages (main branch, /docs)
```

Never edit `docs/` by hand. Edit `src/`, then rebuild.

## Build

```
pip install pillow minify-html
python3 build.py
```

Then commit `src/` and `docs/` together and push. Pages redeploys in a minute or two.

## What the build does

**Responsive images.** Every `<img src="img/...">` in `src/index.html` is
converted to WebP at 400, 800, 1200 and 1800 px wide, plus the original
width, never upscaled past the source. The tag gets `srcset` and a `sizes`
hint for its slot (hero, full-bleed, photo pair, gallery, press card,
thumbnail), so each device downloads only the resolution it needs. A 3x
phone still gets a full-resolution file for full-width photos.

**Quality.** WebP quality 88. Against the original JPEGs this measures
about 40 dB PSNR, which is visually identical. Change `QUALITY` in
`build.py` to trade size for fidelity.

**Cache busting.** Output files are named `<name>.<hash>.<width>.webp`.
The hash covers the source bytes plus the quality and width settings, so
replacing a photo, or changing the settings, always produces a new URL.
GitHub Pages and browsers can never show a stale copy of a swapped photo.

**Hero preload.** The hero image is preloaded with `fetchpriority=high`
so the first screen paints fast.

**Bundling.** HTML, inline CSS and inline JS are minified into a single
`index.html` (about 36 KB). No external JS. The only third-party request
is Google Fonts (Newsreader, Amiri), with preconnect hints.

**Link preview.** `img/preview.jpg` is copied unchanged under its fixed
name. The Open Graph and Twitter tags point at it, and WhatsApp and
iMessage cache previews by URL, so this file must keep its name.

## Results (full scroll, all images loaded)

| Device | Before | After |
| --- | --- | --- |
| Phone, 390 px at 3x | 2.1 MB | 1.1 MB |
| Laptop, 1440 px at 2x | 0.75 MB | 0.68 MB |

Layout is pixel-identical to the unbuilt page at both widths.

## Known limits

- GitHub Pages sets `Cache-Control: max-age=600` on everything and it
  can't be changed. Hashed image names make that irrelevant for photos.
  `index.html` itself can still be up to 10 minutes stale after a push.
- The page is also mirrored as a Claude artifact. Publish the contents
  of `docs/` there after each build.
