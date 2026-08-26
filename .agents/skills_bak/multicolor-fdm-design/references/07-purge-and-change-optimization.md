# Purge and color-change optimization

## The dominant cost is topology over layers

For a single-nozzle material changer, each tool change requires retracting/unloading, loading, purging, and priming. Total cost depends on:

- number of layers containing multiple colors;
- order of colors within each layer;
- transitions between consecutive layers;
- purge volume for every directed color pair;
- tower/poop and transition time.

A design with four colors only in its final three layers may be cheaper than a two-color checkerboard over 500 layers.

## Directed purge matrix

Use a matrix `P[from][to]`. Dark-to-light transitions commonly require more purge than light-to-dark. Tune using a transition coupon at the final temperature and nozzle.

Do not use one symmetric purge value for every pair.

## Design-level reduction methods

Ranked roughly by leverage:

1. move accents into one narrow Z band;
2. print accents as separate inserts;
3. merge tiny islands into neighboring colors;
4. reduce the number of active colors per layer;
5. orient the model so color boundaries become horizontal where acceptable;
6. group repeated objects so the same color sequence is shared;
7. use a dominant base color for hidden internal regions;
8. simplify photographic textures into semantic masks.

## Slicer-level methods

- Tune the purge matrix with physical coupons.
- Use a stable wipe/prime tower and sufficient brim.
- Flush into infill or another object only when contamination cannot show through or weaken a critical region.
- Increase light-colored perimeters if dark purge could show through.
- Keep support material/tool assignment explicit; supports can add hidden changes.
- Inspect actual changes after slicing; visual color count alone is misleading.

## Estimation

The included `estimate_color_changes.py` uses each color part’s Z occupancy to estimate active colors per layer and a conservative lower-bound transition count. It cannot predict every slicer’s exact path order, but it is useful for comparing design variants before slicing.

Outputs include:

- active colors per layer;
- contiguous Z spans per color;
- minimum estimated changes;
- directed purge estimate when a matrix is supplied;
- layers with the highest color complexity.

Use it comparatively: redesign until the estimate falls within the job budget, then confirm with the final slicer.
