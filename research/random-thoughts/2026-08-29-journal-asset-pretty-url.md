# Journal diagrams 404 on GitLab Pages pretty URL

#aea

Related #283. Probe 29 Aug 2026 ~01:03 Europe/Berlin.

`/journal` and `/journal/` serve `journal.html` without redirecting. Relative `src="assets/....jpg"` then requests `/journal/assets/...` (404). The JPEGs are live at `/assets/....jpg` (200, image/jpeg).

From `/journal`, relative nav `schema.html` is `/journal/schema.html` (404, probed). Same class as the diagrams. Builder now root-relatives local `*.html` and `assets/` in wrap, header, and inline links.
