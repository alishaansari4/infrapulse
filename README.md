# InfraPulse: Bias-Corrected Infrastructure Planning Engine

An open-source Digital Public Good (DPG) designed for **Track 1: AI for Digital Public Infrastructure & Governance**.

---

## The Problem
Standard citizen grievance platforms suffer from **voice poverty**: they exclusively capture complaints from citizens with smartphones and digital literacy. Consequently, public budgets get disproportionately funneled to vocal, connected communities, leaving unconnected populations with severe infrastructure gaps invisible.

## The Solution
InfraPulse fuses **bottom-up multilingual feedback** (via Gemini 2.5 Flash) with **top-down objective data** (satellite radiance proxies, census data, and open CapEx budgets). It highlights **Silent Gaps** where need is acute but complaints are absent, computes a transparent **Spend-Need Misalignment Index**, and runs a **Delivery Ledger** to verify post-completion impact.

---

## DPGA 9-Point Self-Assessment (Digital Public Goods Alliance)

1. **Relevance to SDGs:** Contributes directly to SDG 9 (Industry, Innovation & Infrastructure) and SDG 16 (Peace, Justice & Strong Institutions).
2. **Open Source License:** Distributed under the OSI-approved **MIT License**.
3. **Open Standards:** Built on standard CSV/JSON tabular schemas and OpenAPI conventions.
4. **Data Minimization:** Local deterministic regex scrubs phone numbers, Aadhaar patterns, and emails *before* LLM transmission.
5. **Privacy by Design:** Provides zero-knowledge anonymous tokens for whistleblower reporting without storing citizen metadata.
6. **Do No Harm:** Mitigates political astroturfing by corroborating complaints against objective physical satellite signals.
7. **Platform Independence:** Deployable via Docker on any cloud provider or bare-metal server.
8. **Documentation:** Transparent mathematical formulations for all prioritization indices.
9. **Multi-Nation Modularity:** Tested across Indian administrative districts and extensible across BRICS jurisdictions.

---

## Quickstart

```bash
git clone [https://github.com/](https://github.com/)<your-username>/infrapulse.git
cd infrapulse
pip install -r requirements.txt
streamlit run app.py
