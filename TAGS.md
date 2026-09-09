# Controlled tags

Allowed values for `index.jsonl` → `tags[]`. Prefer **these** over inventing new ones.

When tagging a post:
1. Pick 1–4 tags from this list that match the **main claim**.
2. Put products / people / papers in `entities`, not as rogue tags.
3. If nothing fits, use `other` and note why in the gist — then propose a new tag here before using it widely.

Search tip: `python3 tools/search.py --tag <tag>`

---

## Core vocabulary

| Tag | Definition (use when the post is mainly about…) |
|---|---|
| `ai-economics` | Prices, unit economics, CapEx/compute scarcity, labor substitution by agents, markets/moats, funding or allocation of AI capacity |
| `agents` | Agent systems, multi-agent workflows, agent products/frameworks (not every AI demo) |
| `apis` | API design, platform APIs, integration surfaces |
| `cost-optimization` | Reducing model/API/infra spend while holding quality |
| `capacity` | Compute/coding/model capacity as a bottleneck |
| `business-models` | How AI products charge, package, or build moats (tiers, marketplaces, data networks) |
| `funding` | Grants, investment, OSS funding, subsidized access |
| `devtools` | Developer tools, IDEs, agent-browsers, coding agents as tools |
| `code-review` | PR review, CI review agents, human+agent review loops |
| `ci-cd` | Pipelines, on-call automation, deploy/ops agents |
| `systems` | Distributed systems, SSH/remote sessions, infra primitives |
| `frontend` | Web/UI performance and frontend stacks |
| `safety` | AI safety, racing dynamics, lab governance |
| `harness-engineering` | Eval harnesses, agent scaffolding, “harness” as the craft |
| `papers` | Research papers / paper clubs / lit pointers |
| `demos` | Showcases and demos (product flex, not a deep claim) |
| `product-launch` | New product/feature announcements |
| `education` | Teaching, students, university programs |
| `gtm` | Sales, GTM, customer acquisition narratives |
| `mexico` | Mexico / MX–US policy or local context |
| `humor` | Jokes / memes (ok to combine with a serious tag if both fit) |
| `other` | Does not fit above — use sparingly |

Legacy freeform tags already in the index may remain; **new rows should stick to this list**.

---

## `ai-economics` — 5 yes / 5 no

**Definition reminder:** main claim is about money, scarcity, labor substitution, markets, or capacity allocation — not merely “AI did a cool thing.”

### Yes (tag it)

1. **@ClaudeDevs** — prompt caching / effort calibration cutting Claude API cost.  
   https://x.com/ClaudeDevs/status/2097369738968195513  
   *Why:* explicit cost / unit-economics of inference.

2. **@gregisenberg** — niche datasets as a moat; agents pay per query; free/pro/API tiers.  
   *(Sep 7 digest; URL not captured)*  
   *Why:* pricing tiers + data-network business model.

3. **@EMostaque** — 10,000 agents cheaper/faster than humans.  
   https://x.com/EMostaque/status/2097441373200798073  
   *Why:* labor substitution / cost of intelligence at scale.

4. **@zackkanter** — coding capacity more constrained than dialup; gates productivity.  
   *(Sep 7 digest; URL not captured)*  
   *Why:* capacity scarcity as an economic constraint.

5. **@rauchg** — $1,000 OSS grants for agent skills / local AI.  
   *(Sep 7 digest; URL not captured)*  
   *Why:* capital allocation / funding of AI tooling.

### No (do **not** tag `ai-economics`)

1. **@theo** — Astra compiled Melee for Mac at 120 FPS.  
   https://x.com/theo/status/2097435069900341544  
   *Why:* impressive demo, not a pricing/scarcity claim. → `demos`, `agents`

2. **@OpenAI** — claimed Navier–Stokes Millennium Prize via agents.  
   https://x.com/OpenAI/status/2097374640582668336  
   *Why:* research milestone, not economics. → `papers`, `agents`

3. **@mitchellh** — Superlogical remote sessions as SSH alternative.  
   https://x.com/mitchellh/status/2097424868203758046  
   *Why:* systems/devtools, not markets. → `systems`, `devtools`

4. **@sama** — ChatGPT Images 2.5 launch.  
   https://x.com/sama/status/2097410967978324010  
   *Why:* product announcement without pricing/econ thesis. → `product-launch`

5. **@usr_bin_roygbiv** — joke about diverting tokens into a room-temp superconductor.  
   https://x.com/usr_bin_roygbiv/status/2097485733623652751  
   *Why:* humor; token joke ≠ econ analysis. → `humor`

---

## `agents` — 5 yes / 5 no

### Yes
1. @sydneyrunkle — DeepAgents / LangChain / LangGraph when-to-use. https://x.com/sydneyrunkle/status/2097451951906750728
2. @ClaudeDevs — Claude Tag as CI/CD on-call agent. https://x.com/ClaudeDevs/status/2097437571634639035
3. @tonbistudio — Hermes Agent + Omarchy desktop. https://x.com/tonbistudio/status/2097472075393016000
4. @addyosmani — multi-agent first pass on PRs. *(Sep 7; no URL)*
5. @EMostaque — 10k agents cheaper/faster. https://x.com/EMostaque/status/2097441373200798073

### No
1. @usr_bin_roygbiv — React 10MB page joke. https://x.com/usr_bin_roygbiv/status/2097438648404697391 → `frontend`
2. @m_ebrard — Lutnick in CDMX. https://x.com/m_ebrard/status/2097463446103117962 → `mexico`
3. @chrishlad — $1B firm sales story. https://x.com/chrishlad/status/2097483406980313406 → `gtm`
4. @threejs — doodle shooter demo. https://x.com/threejs/status/2096941028297109808 → `demos` / `frontend`
5. @hilbertspaess — lab resignation / safety critique. https://x.com/hilbertspaess/status/2097476196791709843 → `safety` (not “agents” unless agent-specific)

---

## Extending the list

Open a PR / ask AI Researcher to add a tag with: name, one-line definition, 2 yes + 2 no examples. Do not invent one-off tags in digest rows.
