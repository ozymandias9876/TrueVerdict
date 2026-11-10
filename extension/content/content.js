/**
 * TrueVerdict Content Script
 * Extracts product metadata & reviews from active page (DOM & JSON-LD)
 * Fully supports Single Page Applications (SPA), client-side routing, and variant switching.
 */

(function () {
  let lastUrl = window.location.href;
  let cachedData = null;

  async function extractPageData() {
    const url = window.location.href;
    const hostname = window.location.hostname;
    let platform = "generic";

    if (hostname.includes("amazon.")) platform = "amazon";
    else if (hostname.includes("walmart.")) platform = "walmart";
    else if (hostname.includes("target.")) platform = "target";
    else if (hostname.includes("bestbuy.")) platform = "bestbuy";
    else if (document.querySelector("script[src*='shopify'], link[href*='shopify']")) platform = "shopify";

    let product = {
      title: "",
      claimedRating: 0,
      totalReviews: 0,
      platform: platform,
      url: url
    };

    let reviews = [];

    const parseCardsFromRoot = (root) => {
      const cards = root.querySelectorAll('div[data-hook="review"], div.review, [data-testid="review-card"], div[id^="customer_review-"]');
      cards.forEach(card => {
        const titleNode = card.querySelector('[data-hook="reviewTitle"], [data-hook="review-title"], a.review-title, h5');
        let rTitle = titleNode ? titleNode.textContent.trim() : "";
        rTitle = rTitle.replace(/^\d+(?:\.\d+)?\s*(?:out of 5 stars|stars)\s*/i, "").trim();

        let rBody = "";
        const richBody = card.querySelector('[data-hook="reviewRichContentContainer"]');
        if (richBody) {
          rBody = richBody.textContent.trim();
        } else {
          const bodyNode = card.querySelector('[data-hook="reviewText"], [data-hook="review-body"], span.review-text-content');
          if (bodyNode) {
            const clone = bodyNode.cloneNode(true);
            clone.querySelectorAll('.a-teaser-describedby-collapsed, .a-teaser-describedby-expanded').forEach(t => t.remove());
            rBody = clone.textContent.trim();
          }
        }

        if (!rBody && !rTitle) return;

        let rating = 5.0;
        const starNode = card.querySelector('[data-hook="review-star-rating"], i.a-icon-star, span.a-icon-alt');
        if (starNode) {
          const sm = starNode.textContent.match(/(\d(?:\.\d)?)/);
          if (sm) rating = parseFloat(sm[1]);
        }

        const isVerified = Boolean(card.querySelector('[data-hook="avp-badge"]')) || card.textContent.toLowerCase().includes("verified purchase");
        const isIncentivized = card.textContent.toLowerCase().includes("vine customer review of free product");
        const dateNode = card.querySelector('[data-hook="review-date"]');
        const authorNode = card.querySelector('.a-profile-name');

        reviews.push({
          title: rTitle,
          body: rBody,
          rating: rating,
          author: authorNode ? authorNode.textContent.trim() : "Amazon Customer",
          dateStr: dateNode ? dateNode.textContent.trim() : "",
          verified: isVerified,
          incentivized: isIncentivized
        });
      });
    };

    // 1. LIVE DOM EXTRACTION (Highest Priority for SPA / Dynamic Nav)
    if (platform === "amazon") {
      // Visible span#productTitle or hidden input
      const titleSpan = document.querySelector('span#productTitle, #productTitle, h1#title, h1.a-size-large');
      if (titleSpan && titleSpan.textContent.trim().length > 3) {
        product.title = titleSpan.textContent.trim();
      } else {
        const titleInput = document.querySelector('input[name="productTitle"]');
        if (titleInput && titleInput.value && titleInput.value.trim().length > 3) {
          product.title = titleInput.value.trim();
        }
      }

      // Claimed Rating
      const starEl = document.querySelector('#acrPopover span.a-icon-alt, #acrPopover, [data-hook="rating-out-of-text"]');
      if (starEl) {
        const m = starEl.textContent.match(/(\d(?:\.\d)?)\s*(?:out of 5|\/5|stars|\*)/i) || starEl.textContent.match(/(\d(?:\.\d)?)/);
        if (m) product.claimedRating = parseFloat(m[1]);
      }

      // Review Count
      const countEl = document.querySelector('#acrCustomerReviewText, [data-hook="total-review-count"]');
      if (countEl) {
        const m = countEl.textContent.match(/([\d,]+)/);
        if (m) product.totalReviews = parseInt(m[1].replace(/,/g, ''));
      }

      // Review Cards from live DOM
      parseCardsFromRoot(document);

      // Autonomous fallback if cards are lazy loaded below the fold
      if (reviews.length === 0) {
        try {
          const resp = await fetch(window.location.href, { credentials: "same-origin" });
          if (resp.ok) {
            const html = await resp.text();
            const doc = new DOMParser().parseFromString(html, "text/html");
            parseCardsFromRoot(doc);

            if (!product.title) {
              const docTitle = doc.querySelector('span#productTitle, #productTitle');
              if (docTitle) product.title = docTitle.textContent.trim();
            }
            if (product.claimedRating === 0) {
              const docStar = doc.querySelector('#acrPopover span.a-icon-alt, [data-hook="rating-out-of-text"]');
              if (docStar) {
                const m = docStar.textContent.match(/(\d(?:\.\d)?)\s*(?:out of 5|\/5|stars|\*)/i) || docStar.textContent.match(/(\d(?:\.\d)?)/);
                if (m) product.claimedRating = parseFloat(m[1]);
              }
            }
            if (product.totalReviews === 0) {
              const docCount = doc.querySelector('#acrCustomerReviewText, [data-hook="total-review-count"]');
              if (docCount) {
                const m = docCount.textContent.match(/([\d,]+)/);
                if (m) product.totalReviews = parseInt(m[1].replace(/,/g, ''));
              }
            }
          }
        } catch (e) {}
      }
    } else if (platform === "walmart") {
      const titleEl = document.querySelector("h1[itemprop='name'], h1.prod-ProductTitle, #main-title");
      if (titleEl) product.title = titleEl.textContent.trim();

      const cards = document.querySelectorAll("[data-automation-id='review-item'], div.review-item");
      cards.forEach(card => {
        const bodyEl = card.querySelector(".review-text, [itemprop='reviewBody']");
        const body = bodyEl ? bodyEl.textContent.trim() : "";
        if (!body) return;

        reviews.push({
          title: card.querySelector(".review-title")?.textContent.trim() || "",
          body: body,
          rating: 5,
          author: "Walmart Shopper",
          verified: card.textContent.toLowerCase().includes("verified"),
          incentivized: card.textContent.toLowerCase().includes("free")
        });
      });
    }

    // 2. JSON-LD Fallback (Only if reviews or title still missing)
    if (!product.title || reviews.length === 0) {
      const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
      jsonLdScripts.forEach(script => {
        try {
          const data = JSON.parse(script.textContent);
          const items = Array.isArray(data) ? data : (data["@graph"] || [data]);
          items.forEach(item => {
            if (item["@type"] === "Product" || (Array.isArray(item["@type"]) && item["@type"].includes("Product"))) {
              if (item.name && !product.title) product.title = item.name;
              if (item.aggregateRating && product.claimedRating === 0) {
                product.claimedRating = parseFloat(item.aggregateRating.ratingValue || 0);
                product.totalReviews = parseInt(item.aggregateRating.reviewCount || 0);
              }
              if (item.review && reviews.length === 0) {
                const revList = Array.isArray(item.review) ? item.review : [item.review];
                revList.forEach(r => {
                  const body = r.reviewBody || r.description || "";
                  if (body) {
                    reviews.push({
                      title: r.headline || r.name || "",
                      body: body,
                      rating: parseFloat(r.reviewRating?.ratingValue || 5),
                      author: r.author?.name || "Customer",
                      dateStr: r.datePublished || "",
                      verified: true,
                      incentivized: false
                    });
                  }
                });
              }
            }
          });
        } catch (e) {}
      });
    }

    // Fallback title if still empty
    if (!product.title) {
      const h1 = document.querySelector("h1");
      if (h1 && !h1.textContent.toLowerCase().includes("product summary")) {
        product.title = h1.textContent.trim();
      } else {
        const pageTitle = document.title.replace(/\s*[-|:].*$/, "").trim();
        if (pageTitle) product.title = pageTitle;
      }
    }

    cachedData = { product, reviews };
    return cachedData;
  }

  // Update floating badge dynamically
  async function updateFloatingBadge() {
    const data = await extractPageData();
    if (!data.product || !data.product.title) return;

    let badge = document.getElementById("trueverdict-floating-badge");
    if (!badge) {
      badge = document.createElement("div");
      badge.id = "trueverdict-floating-badge";
      document.body.appendChild(badge);
    }

    const reviewCount = data.reviews ? data.reviews.length : 0;
    badge.innerHTML = `
      <div class="tv-badge-icon" style="background:#10b981; color:#fff; font-size:11px; font-weight:800;">✓</div>
      <span>TrueVerdict</span>
      <span class="tv-badge-grade tv-grade-a">${reviewCount > 0 ? 'Active' : 'Ready'}</span>
      <span style="opacity:0.7; font-size:11px;">(${reviewCount} reviews)</span>
    `;

    // Always fetch fresh data on click
    badge.onclick = async () => {
      const latest = await extractPageData();
      alert(`TrueVerdict: Analyzing "${latest.product.title.slice(0, 45)}..." (${latest.reviews.length} reviews parsed).\n\nClick the TrueVerdict icon in your Chrome toolbar for the full breakdown!`);
    };
  }

  // SPA Navigation Watcher
  function checkUrlNavigation() {
    if (window.location.href !== lastUrl) {
      lastUrl = window.location.href;
      cachedData = null; // Invalidate cache immediately on route change!
      setTimeout(updateFloatingBadge, 600);
    }
  }

  // Hook history methods for instant SPA route detection
  const wrapHistory = (type) => {
    const orig = history[type];
    return function () {
      const res = orig.apply(this, arguments);
      checkUrlNavigation();
      return res;
    };
  };

  history.pushState = wrapHistory("pushState");
  history.replaceState = wrapHistory("replaceState");
  window.addEventListener("popstate", checkUrlNavigation);

  // Observe title mutations (common in SPAs)
  const titleEl = document.querySelector("title");
  if (titleEl) {
    new MutationObserver(checkUrlNavigation).observe(titleEl, {
      childList: true,
      characterData: true,
      subtree: true
    });
  }

  // Listen for popup messages
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_PAGE_DATA") {
      extractPageData().then(data => sendResponse(data));
      return true;
    }
    return false;
  });

  // Initial badge setup
  setTimeout(updateFloatingBadge, 1000);
})();
