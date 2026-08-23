# AEA Reference Implementation: Artisanal Bakery Vertical (GAP-V04)

This directory defines the **Artisanal Bakery Industry Adapter** for the Adaptive Experience Architecture (AEA), demonstrating compliance with **`NFR-014 Pin`** (Multi-Domain Retail Portability).

---

## 1. Domain Adaptation & Mapping

The product-neutral runtime foundations (`platform/` and `edge/`) remain unchanged. The domain adapter provides specialized facet keys and catalog schemas:

| AEA Platform Concept | Lily's Florist (Reference Design) | Artisanal Bakery (Adapter) |
|---|---|---|
| **Tile T-01 Discovery** | Flowers, Occasion, Recipient, Budget | Custom Cake, Pastry Box, Event, Servings |
| **Tile T-02 Interpretation** | Flower Preferences, Delivery Date | Dietary/Allergen Exclusions, Pickup Window |
| **Tile T-04 Selection** | Stem Count, Card Message, Ribbon | Cake Tier Size, Custom Icing Inscription, Piping |
| **Tile T-05 Delivery** | Home Address, Morning/Afternoon Slot | Bakery Store Pickup, Chilled Courier Delivery |

---

## 2. Dynamic Allergen & Dietary Safety Exclusions

* **`gluten_free`**: Excludes items containing wheat flour.
* **`nut_free`**: Excludes items produced in facilities with tree nuts or peanuts.
* **`vegan`**: Excludes items containing dairy, eggs, or honey.
