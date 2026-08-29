# Journal

A short public history of Adaptive Experience Architecture: what was hard, what we solved, what shipped, and what we learned. Not a ticket dump. Not a daily log.

## Why this started

**Challenge.** A florist asked for a website that could take more orders, keep inventory straight, and offer generative support at all hours. The easy mistake is to copy that ask as a feature list.

**Solve.** It began as a Quantic Managing AI Engineering project: interview the proprietor, write stories and a journey, then requirements and annotated mockups. The group delivery (Meghna Desai, Hiren Vadalia, Claude Tsarafidy) turned that into one adaptive workspace. Conversation stays in place. The assistant may interpret. Dedicated services still decide catalog, inventory, price, delivery, payment, and the order.

**Ship.** The original functional view named eight tiles on a topic bus and stayed implementation-neutral so wireframes and services could move together. That view is the ancestor of the live florist, not the live florist. The course asked for a PDF and Figma. What lasted is the split, plus a later harness: two hostnames, and a rule that a status word is a claim until a probe.

**Lesson.** The customer's ask is an interview, not the spec. The course ended at a packet. What followed is the shop you can open and the framework that refuses to treat a closed ticket as a clip. Payment is still a mockup. After the dual-viewport CSS landed, a fresh clip is still Unknown.

![From a course brief to a group delivery to a live shop and a public framework](assets/origin-brief.svg)

## Claim vs probe

**Challenge.** Status words started standing in for evidence. "Verified" and "shipped" felt finished because a ticket closed.

**Solve.** A status word is a claim. In the same session, point at a probe, or write Unknown.

**Ship.** The live florist taught that a merged change is not a clip.

**Lesson.** Closing a tracker is not a clip. Probe the same journey on both a phone and a desktop, or leave it Unknown.

![Claim vs probe: a merged ticket is not verified until the same journey is probed on phone and desktop](assets/claim-vs-probe.svg)

## Two hostnames

**Challenge.** One product looked like one website. It is not.

**Solve.** The framework lives at architecture.artof.link. The florist shop stays at aea.artof.link. Merge publishes the first. The shop has its own host.

**Ship.** The framework site is markdown on GitLab main, rebuilt by Pages. No CMS. DNS can be live while the public page is still private, and a verified domain is not yet a certificate.

**Lesson.** Merge is not "the site is up." Two hostnames, two jobs.

![Two hostnames: framework Pages versus the live shop](assets/two-hostnames.svg)

## Four lines, one day

**Challenge.** The first story about the florist was wrong. Failures stacked. Green boards hid that.

**Solve.** Name the journeys. Treat a clip as evidence, not theater. When the first hypothesis dies, write that down instead of restyling the shop.

**Ship.** Four named journeys on the live shop, on two viewports. Dual-viewport is the intended presentation. After the CSS landed, a fresh clip is still Unknown, so the case study stays honest: not verified.

**Lesson.** Written must match implemented. The first line can be wrong. The work is to notice, not to decorate.

![Four named journeys, one live shop, two viewports](assets/four-lines.svg)

## How this journal stays honest

- Curated episodes only. No daily dump.
- Pictures that explain a lesson. No screenshot gallery of the shop.
- If a later check is missing, the page says so. It does not borrow a status from chat.
- Third-party course or paper text is our paraphrase, or a short marked quote with a source. Packets stay off this site.

Back to the [framework](index.html), the [schema](schema.html), the [comparison](comparison.html), or the [Path B case study](path-b.html).
