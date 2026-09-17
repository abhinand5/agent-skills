# Kindle PDF reflow QA

## Choosing the trial

Prefer 16 contiguous source pages containing ordinary prose plus at least one figure,
caption, displayed equation, and boxed algorithm. `--pages auto` starts at about 8.5%
of the source; override it when that window is front matter, references, or unusually
sparse. A contiguous range matters because it exposes real page-flow behavior.

On the trial, compare a known paragraph rather than judging font size alone. Count its
rendered lines and compare how much of the readable page it occupies. Also compare the
number of ordinary body lines per screen and the usable horizontal measure.

## Tall vertical rules

k2pdfopt can treat a tall proof border or derivation rule as one graphic and slice a
line. `-evl 1` avoids that failure, but applying it globally can erase legitimate
vertical distributions and plot elements. Identify the affected *source* pages, pass
only those through `--special-pages`, and visually inspect both the repaired pages and
nearby figures.

## Required visual checks

- Render all pages as thumbnails and inspect every contact sheet for blank pages,
  abrupt density changes, oversized graphics, or suspicious fragments.
- Open at native resolution: cover, contents, first page of every major part/chapter,
  several equation-heavy pages, several figures, several algorithm boxes, the first
  references page, the first index page, every verifier-reported thin page, and the
  final page.
- Re-open the exact paragraph used to approve the trial and ensure its line count is
  unchanged in the full build.
- Check that top-level outline destinations land on their named headings.

## Interpreting verification

The source's text map may already be imperfect, especially for mathematical fonts.
Rare-word misses can therefore be invisible-text-layer defects even when the words are
visually present. Investigate a small miss set visually; reject a build for widespread
loss, blank pages, inconsistent geometry, damaged figures, or edge clipping.

A page with fewer than 40 extracted characters is not necessarily blank. Reflow can
leave a final equation line, exercise fragment, reference year, or index continuation
on a mostly white screen. Inspect each reported thin page rather than deleting it.

## Dependencies

The builder needs Python 3, PyMuPDF, and k2pdfopt 2.55 or compatible. The deep verifier
also needs NumPy. Poppler (`pdfinfo`, `pdftoppm`) and ImageMagick `montage` are used for
rendering and contact sheets.
