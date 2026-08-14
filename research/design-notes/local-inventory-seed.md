# Local inventory seeder and open-data alternatives

Issue: [#169](https://gitlab.com/artof-group/adaptive-experience-architecture/-/issues/169).
Status: accepted as a **local/dev** fixture, not an Architecture Decision Record.

## Why a synthetic seeder

FR-011 / NFR-009 treat missing or older-than-one-minute
`inventory.product_availability` rows as **unknown**. Selection fails closed
unless the product is currently available. The Lily's Florist reference catalog
(`classic-rose-dozen`, `lilac-bouquet`, `budget-mixed-bunch`, `pink-flower-vase`,
`premium-orchid`) is a ranking fixture (FR-007), not a Catalog SoT, and local
`edge/docker-compose.yml` has no POS or warehouse feed.

The compose `inventory-seeder` sidecar (`AEA_SEED_INVENTORY=1`) therefore writes
monotonic, versioned snapshots with `available_quantity > 0` and refreshes
`observed_at` about every 30 seconds. Production must omit the sidecar. A
one-shot INSERT at boot is not enough: the freshness window is one minute.

This seeder does **not** replace inventory authority and must not run when
`AEA_ENVIRONMENT=production`.

## Our World in Data is not a florist catalog

[Our World in Data](https://ourworldindata.org/) publishes global development,
health, energy, environment, and **food/agriculture** series (crop yields,
cereal production, coffee, land use). Charts and articles are CC BY 4.0; many
series are processed FAOSTAT and remain under the **original source licence**.
There is no florist SKU catalog, no cut-flower availability feed, and no
`classic-rose-dozen`-style product IDs. Searches for flowers, cut flowers,
horticulture, and roses on OWID surface food-crop and land-use topics, not
floriculture SKUs.

OWID / FAO series can later inform **optional supply-signal research** (seasonal
production pressure, country-level crop volume). They cannot map 1:1 onto
`product_id` + `available_quantity` + `source_version` for T-03 Select.

## Alternatives for inventory-like signals

Keep the **local seeder synthetic** for Lily's Florist reference SKUs. Treat
the rows below as research inputs, not a drop-in seed. Do not bulk-download
these dumps into the repo.

| Source | What it can supply | Maps to `product_id` + `available_quantity` + `source_version`? | Licence / terms |
|---|---|---|---|
| **Synthetic reference seeder** (this change) | Fresh available quantities for the five FR-007 ranking SKUs | Direct: seed those IDs, qty > 0, monotonic `source_version`, UTC `observed_at` | Internal fixture only |
| **POS / warehouse / inventory feed** (authoritative for FR-011) | On-hand units per sellable SKU, versions, observation time | Direct: this is the production mapping | Operator contract |
| [Our World in Data](https://ourworldindata.org/) agricultural production / [crop yields](https://ourworldindata.org/crop-yields) | Country/year food-crop volume and yield (cereals, fruit, coffee, …) | No SKU. At best a coarse regional supply-pressure signal after a researched mapping | OWID charts CC BY 4.0; underlying FAO/other licences apply |
| [FAOSTAT QCL](https://www.fao.org/faostat/en/#data/QCL) crop production | National production, area, yield for food/feed crops | Ornamental cut flowers are generally **outside** the food-crop domain. Not a store inventory | FAO terms; attribution required |
| [USDA NASS Floriculture Crops](https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Floriculture/) / horticultural census | US grower counts, area, quantity sold, prices for cut flowers, potted plants, etc. | Species/category and wholesale volume, not Lily's SKUs. Could inform seasonality research | US public domain; cite USDA-NASS |
| UN Comtrade / HS 0603 (cut flowers; 0603.11 roses, 0603.12 carnations, 0603.13 orchids) | International trade value/quantity by country | Import/export flows, not on-hand store units | UN Comtrade terms |
| [AIPH](https://aiph.org/) International Statistics Flowers and Plants | Industry floriculture production and trade tables | Closer to cut-flower markets; still not a SKU availability API | Typically paid / all rights reserved — not an open dump |
| Open Food Facts | Packaged food products | Poor fit for florist SKUs | ODbL / contributor terms |
| Wikidata flora / [GBIF](https://www.gbif.org/) | Species taxonomy and occurrence | Species, not sellable bouquets | CC0 / CC BY depending on dataset |

Recommended mapping if a future research job ever uses a supply series:

- `product_id` stays the reference (or Catalog) SKU; join via an explicit
  species/category table (`roses` → `classic-rose-dozen`), never via dataset
  entity names alone.
- `available_quantity` stays on-hand units from inventory authority. Open data
  may only adjust a **research heuristic** (for example, mark a category as
  seasonal). It must not override fail-closed selection.
- `source_version` stays the inventory feed's monotonic version (or the local
  seeder's increment). An OWID/FAO release year is metadata, not
  `source_version`.
