# ADR-020 Layer 2 — Edge Wallet implementation

> Companion to [`docs/06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md`](../../docs/06-adr/ADR-020-privacy-preserving-crm-and-edge-wallet.md).
> Scope: the device-owned Edge Wallet in the Android companion
> (`clients/mobile/android`). Enables FR-008 one-tap reorder without a
> server-side PII CRM (ADR-013 / NFR-017).

## Zero-PII boundary (the key idea)

Device-only convenience data (recipient label such as "Mom", card message
draft, occasion month/day) is encrypted at rest on the device and **never**
leaves it. Only opaque references (`product_id`, `order_reference`) are ever
surfaced back to the platform for a reorder — enforced structurally by
`ReorderReference`, which cannot carry a label, card, address, or payment.

```mermaid
flowchart LR
  subgraph Device["📱 Android device (owner-held)"]
    direction TB
    UI["Compose UI\n(Pay / Tracking / Reorder)"]
    Repo["SessionRepository"]
    Wallet["EdgeWallet\n(pure Kotlin domain)"]
    Store["WalletStore (port)"]
    Enc["EncryptedPrefsWalletStore\nEncryptedSharedPreferences"]
    KS["Android Keystore\nAES-256 master key"]
    Receipts["WalletReceipt[]\n(orderRef, productId,\nrecipientLabel*, cardDraft*,\noccasion*)\n* device-only"]

    UI --> Repo --> Wallet --> Store --> Enc --> KS
    Enc -. encrypts at rest .-> Receipts
  end

  subgraph Platform["☁️ AEA platform (zero-PII)"]
    direction TB
    BFF["Edge BFF\n/api/v1/selection"]
    Orch["Orchestration + Postgres"]
  end

  Repo -- "ReorderReference\n{product_id, order_reference}\nOPAQUE ONLY" --> BFF --> Orch

  classDef deviceOnly fill:#1b4332,stroke:#2d6a4f,color:#fff;
  classDef platform fill:#1d3557,stroke:#457b9d,color:#fff;
  class Receipts,Wallet,Store,Enc,KS deviceOnly;
  class BFF,Orch platform;
```

## Components

| Layer | Type | Android? | Responsibility |
|---|---|---|---|
| Domain | `EdgeWallet` | No (pure Kotlin) | Save/dedup receipts, pick latest, derive **opaque-only** `ReorderReference`, clear |
| Model | `WalletReceipt` / `ReorderReference` | No | Receipt carries device-only fields; `ReorderReference` is opaque-only by construction |
| Port | `WalletStore` | No | `load()` / `save()` persistence seam |
| Adapter | `InMemoryWalletStore` | No | Safe default (tests / non-Android construction) |
| Adapter | `EncryptedPrefsWalletStore` | Yes | `EncryptedSharedPreferences` + Keystore AES-256 at rest; JSON (de)serialization |
| Wiring | `SessionRepository` | No (Context injected at edge) | Writes a receipt on successful checkout; exposes reorder read/action |
| Entry | `MainActivity` | Yes | Injects `EdgeWallet(EncryptedPrefsWalletStore(applicationContext))` |

Keeping the domain Android-free is deliberate: the reorder / zero-PII logic is
unit-testable on the plain JVM, while only the thin encryption adapter needs
the Android runtime.

## Write path — record a receipt after checkout

```mermaid
sequenceDiagram
  autonumber
  participant U as Customer
  participant R as SessionRepository
  participant B as Edge BFF
  participant W as EdgeWallet
  participant E as EncryptedPrefsWalletStore
  U->>R: completeCheckout(cardMessage)
  R->>B: selection / delivery / order / checkout (opaque refs only)
  B-->>R: confirmed order_id + total
  R->>W: saveReceipt(orderId, productId, recipientLabel*, cardDraft*, occasion*)
  W->>E: save(receipts)  %% *device-only fields
  E->>E: encrypt (Keystore AES-256) → EncryptedSharedPreferences
  Note over R,B: recipientLabel / cardDraft never sent to platform
```

## Read path — FR-008 one-tap reorder

```mermaid
sequenceDiagram
  autonumber
  participant U as Returning customer
  participant R as SessionRepository
  participant W as EdgeWallet
  participant B as Edge BFF
  U->>R: reorderFromWallet()
  R->>W: reorderReference()
  W-->>R: ReorderReference{product_id, order_reference}  %% opaque only
  R->>B: POST /api/v1/selection {product_id}
  B->>B: authoritative inventory revalidation (NFR-009 fail-closed)
  B-->>R: accepted (or product_unavailable)
  Note over W,B: no recipient label / card / address / payment crosses the boundary
```

## Test strategy

- Pure-domain JVM tests: receipt round-trip + dedup, latest ordering, and the
  **zero-PII invariant** that `ReorderReference` exposes only opaque ids.
- Repository test: a confirmed checkout writes exactly one wallet receipt and
  `reorderFromWallet()` re-selects the stored opaque `product_id`.
- Encryption adapter (`EncryptedPrefsWalletStore`) is Android-runtime bound and
  is covered by instrumented/`androidTest` scope, not JVM unit tests.
