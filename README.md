# 🛡️ TrueVerdict

> **The Honest Review & 6-Month Durability Reality for E-Commerce**  
> *Expose fake reviews, uncover what breaks after Month 2, and check Reddit community consensus on Amazon, Walmart, and any store.*

![TrueVerdict Preview](docs/popup_preview.png)

[![Manifest V3](https://img.shields.io/badge/Manifest-V3-10b981.svg)](https://developer.chrome.com/docs/extensions/mv3/intro/)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-blue.svg)](#-privacy-first-guarantee)
[![Affiliate Kickbacks](https://img.shields.io/badge/Affiliate%20Kickbacks-0%25-red.svg)](#-zero-affiliate-bias)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⚡ Why TrueVerdict?

Most products on Amazon, Walmart, and modern marketplaces boast a **4.8★ rating** on day one.  
...Until they stop working on **Day 62**, immediately after the 30-day return window closes.

Modern review manipulation has evolved far beyond obvious bad grammar:
- **Review Syndicates**: Brands pay coordinated bot networks to copy-paste identical promotional phrases across dozens of accounts.
- **Incentivized Vine Flooding**: Hundreds of free-product reviews drown out genuine paying customers.
- **Early-Death Defects**: Products engineered to survive only the first 30 days before critical component fatigue sets in.

**TrueVerdict is an open, 100% client-side Chrome extension** that recalculates the honest durability of any product before you checkout.

---

## 🚀 Key Features

### 1. 🛡️ Review Syndicate Detection
Algorithms extract 6-word sentence shingles across the review corpus. If multiple accounts share verbatim recycled sentences (*e.g., promotional copy distributed by review farms*), TrueVerdict flags the coordinated manipulation and adjusts the rating accordingly.

### 2. ⏳ The "6-Month Reality"
Our temporal NLP parser identifies reported failures across critical milestones:
- **0 – 30 Days**: Out-of-box defects & initial setup failures
- **1 – 3 Months**: Early wear, charging port failures, and structural fatigue
- **3 – 6 Months**: Material degradation, peeling, and hinge cracks
- **6 – 12 Months**: Long-term durability consensus

### 3. 💬 Organic Reddit Community Consensus
Cross-references real consumer discussions from enthusiast subreddits like `r/BuyItForLife`, `r/headphones`, and `r/gadgets`.  
- **Honest Brand Handling**: If an unlisted marketplace product has no organic Reddit discussion, TrueVerdict explicitly marks it as **Unlisted Brand** without fabricating quotes.

### 4. 🔒 Privacy-First & Zero Affiliate Bias
- **Zero Affiliate Links**: We take zero commissions from Amazon or brand referrals. We have zero financial incentive to convince you to buy.
- **100% Local Execution**: All extraction and analysis run in your browser sandbox. Your browsing history is never transmitted to remote servers.

---

## 📥 Installation

### Method 1: Load Unpacked in Chrome (Developer Mode)

1. Clone or download this repository:
   ```bash
   git clone https://github.com/ozymandias9876/TrueVerdict.git
   ```
2. Open Google Chrome and navigate to `chrome://extensions`.
3. Toggle **Developer mode** on in the top-right corner.
4. Click **Load unpacked** in the top-left corner.
5. Select the `extension/` folder from this repository.
6. Open any product page on Amazon (*e.g., amazon.com or amazon.in*) and click the **TrueVerdict** icon in your toolbar!

### Method 2: Packaged ZIP

Download the pre-packaged distribution file [`dist/TrueVerdict-v1.0.1.zip`](dist/TrueVerdict-v1.0.1.zip), unzip it, and load it via `chrome://extensions`.

---

## 📂 Repository Structure

```
TrueVerdict/
├── extension/                 # Chrome Extension (Manifest V3)
│   ├── manifest.json          # Extension configuration
│   ├── popup/                 # Extension popup UI & client-side analyzer
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   ├── content/               # SPA-aware content script & floating badge
│   │   ├── content.js
│   │   └── content.css
│   └── icons/                 # Extension icons (16px, 48px, 128px)
├── src/                       # Python analytical engine & benchmark models
│   ├── authenticity.py        # Syndicate & bot pattern detection
│   ├── durability_engine.py   # Temporal failure & hardware flaw parsing
│   ├── reddit_checker.py      # Community consensus verification
│   └── synthesis.py           # Unified verdict scoring
├── tests/                     # Playwright & unit test suite
├── video/                     # 20-second product launch video (Remotion)
├── dist/                      # Web Store ready distribution ZIP
└── docs/                      # Screenshots & assets
```

---

## ☕ Support Independent Tech

TrueVerdict is free and takes zero affiliate kickbacks. If this tool saved you from buying a broken product, consider supporting development:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-$3-orange.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/trueverdict)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
