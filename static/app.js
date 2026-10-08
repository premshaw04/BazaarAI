// ==========================================================================
// BazaarAI — Client-Side Application Logic (Home & Chat Views with SQLite History)
// ==========================================================================

const state = {
  currentSessionId: null,
  currentView: "home",
  messages: [],
  cart: [
    {
      id: 101,
      name: "Nike Revolution 7",
      price: 2799,
      image: "/static/images/nike_revolution_7.jpg",
      quantity: 1,
    },
    {
      id: 102,
      name: "Adidas Galaxy 6",
      price: 2499,
      image: "/static/images/adidas_galaxy_6.jpg",
      quantity: 1,
    },
    {
      id: 103,
      name: "Puma Softride Enzo",
      price: 2699,
      image: "/static/images/puma_softride_enzo.jpg",
      quantity: 1,
    },
  ],
  wishlist: new Set(),
  activeFilters: {
    brand: "all",
    rating: "all",
    price: "all",
  },
};

// DOM Elements
const homeView = document.getElementById("homeView");
const chatView = document.getElementById("chatView");
const navHome = document.getElementById("navHome");
const chatContainer = document.getElementById("chatContainer");
const dynamicMessagesContainer = document.getElementById("dynamicMessagesContainer");
const chatTextInput = document.getElementById("chatTextInput");
const sendMessageBtn = document.getElementById("sendMessageBtn");
const attachImageBtn = document.getElementById("attachImageBtn");
const hiddenFileInput = document.getElementById("hiddenFileInput");
const cartBadgeCount = document.getElementById("cartBadgeCount");
const recentChatsList = document.getElementById("recentChatsList");
const newChatBtn = document.getElementById("newChatBtn");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

// Hero Search Elements
const heroSearchInput = document.getElementById("heroSearchInput");
const heroSendBtn = document.getElementById("heroSendBtn");
const heroClipBtn = document.getElementById("heroClipBtn");
const heroMicBtn = document.getElementById("heroMicBtn");

// Modals & Drawers
const productModal = document.getElementById("productModal");
const productModalBody = document.getElementById("productModalBody");
const cartDrawer = document.getElementById("cartDrawer");
const cartItemsList = document.getElementById("cartItemsList");
const cartSubtotalText = document.getElementById("cartSubtotalText");
const cartTotalText = document.getElementById("cartTotalText");
const shopByImageModal = document.getElementById("shopByImageModal");
const settingsModal = document.getElementById("settingsModal");
const searchPaletteModal = document.getElementById("searchPaletteModal");
const paletteSearchInput = document.getElementById("paletteSearchInput");

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  updateCartUI();
  checkSettingsStatus();
  loadChatHistory();
  initNewSessionId();
});

function initNewSessionId() {
  state.currentSessionId = "chat_" + Date.now();
}

// ==========================================================================
// VIEW ROUTING (HOME vs CHAT)
// ==========================================================================

function switchView(viewName) {
  state.currentView = viewName;
  if (viewName === "home") {
    homeView.classList.add("active");
    homeView.style.display = "flex";
    chatView.classList.remove("active");
    chatView.style.display = "none";
    if (navHome) navHome.classList.add("active");
  } else {
    homeView.classList.remove("active");
    homeView.style.display = "none";
    chatView.classList.add("active");
    chatView.style.display = "flex";
    if (navHome) navHome.classList.remove("active");
    scrollToBottom();
  }
}

function startNewChat() {
  initNewSessionId();
  state.messages = [];
  dynamicMessagesContainer.innerHTML = "";
  switchView("home");
  loadChatHistory();
  showToast("✨ Started a new shopping session");
}

function startChatWithQuery(query) {
  switchView("chat");
  handleSendMessage(query);
}

// ==========================================================================
// EVENT LISTENERS
// ==========================================================================

function setupEventListeners() {
  // Navigation Home click
  if (navHome) {
    navHome.addEventListener("click", (e) => {
      e.preventDefault();
      switchView("home");
    });
  }

  // New Chat button in sidebar
  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => startNewChat());
  }

  // Clear History button
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => clearAllChatHistory());
  }

  // Hero Search in Home View
  if (heroSendBtn && heroSearchInput) {
    heroSendBtn.addEventListener("click", () => {
      const q = heroSearchInput.value.trim();
      if (q) {
        heroSearchInput.value = "";
        startChatWithQuery(q);
      }
    });

    heroSearchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const q = heroSearchInput.value.trim();
        if (q) {
          heroSearchInput.value = "";
          startChatWithQuery(q);
        }
      }
    });
  }

  if (heroClipBtn) {
    heroClipBtn.addEventListener("click", () => openShopByImageModal());
  }

  if (heroMicBtn) {
    heroMicBtn.addEventListener("click", () => triggerVoiceSearch());
  }

  // Chat page Send button & Enter key
  sendMessageBtn.addEventListener("click", () => handleSendMessage());
  chatTextInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Suggestion chips in chat page
  document.querySelectorAll(".chip-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const query = btn.getAttribute("data-query");
      handleSendMessage(query);
    });
  });

  // Wishlist heart buttons on cards
  document.querySelectorAll(".favorite-heart-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute("data-id"));
      toggleWishlist(id, btn);
    });
  });

  // Shop by Image buttons
  attachImageBtn.addEventListener("click", () => openShopByImageModal());
  const navShopByImage = document.getElementById("navShopByImage");
  if (navShopByImage) {
    navShopByImage.addEventListener("click", (e) => {
      e.preventDefault();
      openShopByImageModal();
    });
  }

  // Cart Drawer buttons
  document.getElementById("openCartBtn").addEventListener("click", () => openCartDrawer());

  // Database Catalog & Orders
  const navCategories = document.getElementById("navCategories");
  if (navCategories) {
    navCategories.addEventListener("click", (e) => {
      e.preventDefault();
      openDatabaseModal();
    });
  }

  const navOrders = document.getElementById("navOrders");
  if (navOrders) {
    navOrders.addEventListener("click", (e) => {
      e.preventDefault();
      openOrdersModal();
    });
  }

  // Settings button
  document.getElementById("openSettingsBtn").addEventListener("click", () => openSettingsModal());

  // Command palette shortcut ⌘K / Ctrl+K
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      openSearchPalette();
    }
    if (e.key === "Escape") {
      closeAllModals();
    }
  });

  const searchChatsBtn = document.getElementById("searchChatsBtn");
  if (searchChatsBtn) {
    searchChatsBtn.addEventListener("click", () => openSearchPalette());
  }

  // File dropzone
  const dropZone = document.getElementById("dropZone");
  if (dropZone) {
    dropZone.addEventListener("click", () => hiddenFileInput.click());
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      if (e.dataTransfer.files.length > 0) {
        uploadAndSearchImage(e.dataTransfer.files[0]);
      }
    });
  }

  hiddenFileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      uploadAndSearchImage(e.target.files[0]);
    }
  });
}

function triggerVoiceSearch() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("Voice search not supported in this browser");
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  showToast("🎙️ Listening... speak now");
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    heroSearchInput.value = transcript;
    startChatWithQuery(transcript);
  };
  recognition.onerror = () => {
    showToast("Could not recognize voice");
  };
  recognition.start();
}

// ==========================================================================
// CHAT HISTORY (REAL SQLITE STORAGE & RETRIEVAL)
// ==========================================================================

async function loadChatHistory() {
  try {
    const res = await fetch("/api/chats");
    const data = await res.json();
    const chats = data.chats || [];

    if (!chats.length) {
      recentChatsList.innerHTML = `<div class="empty-chats-hint">No recent chats yet. Start a conversation!</div>`;
      return;
    }

    recentChatsList.innerHTML = chats
      .map(
        (c) => `
        <div class="chat-history-item ${c.id === state.currentSessionId ? "active" : ""}" onclick="loadChatSession('${c.id}')">
          <span class="chat-title" title="${escapeHtml(c.title)}">${escapeHtml(c.title)}</span>
          <span class="chat-time">${c.time_ago}</span>
          <button class="chat-del-btn" title="Delete chat" onclick="deleteChatSession(event, '${c.id}')">×</button>
        </div>
      `
      )
      .join("");
  } catch (err) {
    console.error("Error loading chat history:", err);
  }
}

async function loadChatSession(sessionId) {
  try {
    const res = await fetch(`/api/chats/${sessionId}`);
    const session = await res.json();

    state.currentSessionId = session.id;
    state.messages = session.messages || [];

    // Switch to Chat View
    switchView("chat");

    // Render messages
    dynamicMessagesContainer.innerHTML = "";
    for (const msg of state.messages) {
      if (msg.role === "user") {
        renderUserMessage(msg.content, msg.timestamp || getCurrentTime(), msg.image_url || null);
      } else {
        renderAiResponse(msg);
      }
    }

    loadChatHistory();
    scrollToBottom();
  } catch (err) {
    showToast("Error loading conversation");
  }
}

async function deleteChatSession(e, sessionId) {
  e.stopPropagation();
  try {
    await fetch(`/api/chats/${sessionId}`, { method: "DELETE" });
    if (state.currentSessionId === sessionId) {
      startNewChat();
    } else {
      loadChatHistory();
    }
    showToast("Chat removed from history");
  } catch (err) {
    showToast("Error deleting chat");
  }
}

async function clearAllChatHistory() {
  if (!confirm("Are you sure you want to clear all chat history?")) return;
  try {
    await fetch("/api/chats", { method: "DELETE" });
    startNewChat();
    showToast("All chat history cleared");
  } catch (err) {
    showToast("Error clearing chat history");
  }
}

// ==========================================================================
// CHAT MESSAGING ENGINE
// ==========================================================================

async function handleSendMessage(customText = null, imageAttachment = null) {
  const text = (customText || chatTextInput.value).trim();
  if (!text && !imageAttachment) return;

  chatTextInput.value = "";
  const timeStr = getCurrentTime();

  // If in Home View, switch to Chat View
  if (state.currentView !== "chat") {
    switchView("chat");
  }

  // Ensure valid session ID
  if (!state.currentSessionId) {
    initNewSessionId();
  }

  const userDisplayText = text || "Find products similar to this uploaded photo";
  const userImageUrl = imageAttachment ? (imageAttachment.url || null) : null;
  const userImagePath = imageAttachment ? (imageAttachment.local_path || null) : null;

  // 1. Render User Message
  renderUserMessage(userDisplayText, timeStr, userImageUrl);
  state.messages.push({
    role: "user",
    content: userDisplayText,
    timestamp: timeStr,
    image_url: userImageUrl,
    image_path: userImagePath,
  });

  // 2. Render Loading Assistant Bubble
  const loadingRow = renderLoadingBubble();
  scrollToBottom();

  try {
    const payload = {
      message: userDisplayText,
      history: state.messages,
      session_id: state.currentSessionId,
    };
    if (userImagePath) {
      payload.image_path = userImagePath;
    }
    if (userImageUrl) {
      payload.image_url = userImageUrl;
    }

    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    loadingRow.remove();

    renderAiResponse(data);
    state.messages.push({
      role: "assistant",
      content: data.content,
      products: data.products,
      timestamp: data.timestamp || timeStr,
    });

    // Update real chat history sidebar!
    loadChatHistory();
  } catch (err) {
    console.error("Chat error:", err);
    loadingRow.remove();
    renderAiResponse({
      content: "I'm sorry, an error occurred while processing your request. Please try again.",
      products: [],
      timestamp: timeStr,
    });
  }

  scrollToBottom();
}

function renderUserMessage(text, timeStr, imagePreviewUrl = null) {
  const row = document.createElement("div");
  row.className = "message-row user-row";
  const imgHtml = imagePreviewUrl ? `
    <div class="user-chat-img-wrap">
      <img src="${escapeHtml(imagePreviewUrl)}" alt="Uploaded Photo" class="user-chat-img-thumbnail">
    </div>
  ` : "";

  row.innerHTML = `
    <div class="message-bubble-wrapper">
      <div class="message-bubble user-bubble">
        ${imgHtml}
        <div class="user-bubble-content">
          <span class="user-text">${escapeHtml(text)}</span>
          <div class="message-meta">
            <span class="message-time">${timeStr}</span>
            <span class="read-receipt">✓✓</span>
          </div>
        </div>
      </div>
    </div>
    <div class="avatar user-avatar-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    </div>
  `;
  dynamicMessagesContainer.appendChild(row);
}

function renderLoadingBubble() {
  const row = document.createElement("div");
  row.className = "message-row ai-row loading-row";
  row.innerHTML = `
    <div class="avatar ai-avatar">
      <img src="/static/images/bazaar_emblem.jpg" alt="BazaarAi" class="avatar-emblem-img">
    </div>
    <div class="message-bubble-wrapper">
      <div class="message-bubble ai-bubble">
        <span style="color: #9c968c;">Searching catalog & analyzing best matches…</span>
      </div>
    </div>
  `;
  dynamicMessagesContainer.appendChild(row);
  return row;
}

// Toggle Agent Execution Trace Accordion
window.toggleAgentTrace = function(traceId) {
  const el = document.getElementById(traceId);
  if (el) {
    el.classList.toggle("open");
  }
};

function buildAgentTraceHtml(trace, traceId) {
  if (!trace || !trace.steps || trace.steps.length === 0) return "";
  const toolCount = trace.tools_used ? trace.tools_used.length : trace.steps.length;
  const timeMs = trace.duration_ms || 120;
  const modeText = trace.mode || "Autonomous Agent";

  const stepsHtml = trace.steps.map((s) => `
    <div class="agent-step-item">
      <div class="step-header">
        <span class="step-num-badge">Step ${s.step}</span>
        <span class="tool-tag">⚡ ${escapeHtml(s.tool)}</span>
      </div>
      <div class="step-thought">
        <span class="step-thought-label">Thought:</span> ${escapeHtml(s.thought || "")}
      </div>
      ${s.args && Object.keys(s.args).length > 0 ? `
        <div class="step-action-row">
          <span style="color: #8f897e; font-size: 11px;">Parameters:</span>
          <code class="tool-args">${escapeHtml(JSON.stringify(s.args))}</code>
        </div>
      ` : ""}
      <div class="step-observation">
        <strong>Observation:</strong> ${escapeHtml(s.observation || "")}
      </div>
    </div>
  `).join("");

  return `
    <div class="agent-trace-box" id="${traceId}">
      <div class="agent-trace-header" onclick="toggleAgentTrace('${traceId}')">
        <div class="agent-trace-title">
          <span class="trace-brain-icon">🧠</span>
          <span>Agent Reasoning & Tool Execution</span>
          <div class="trace-pills-wrap">
            <span class="trace-pill-badge">${toolCount} tool${toolCount > 1 ? "s" : ""}</span>
            <span class="trace-pill-time">${timeMs}ms</span>
          </div>
        </div>
        <div class="trace-toggle-btn">
          <span>View Steps</span>
          <svg class="chevron-trace" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </div>
      </div>
      <div class="agent-trace-body">
        <div class="agent-plan-row">
          <strong>Autonomous Plan:</strong> ${escapeHtml(trace.plan || "Executing intent")} &nbsp;•&nbsp; <em style="color: #f5b665;">${escapeHtml(modeText)}</em>
        </div>
        <div class="agent-steps-timeline">
          ${stepsHtml}
        </div>
      </div>
    </div>
  `;
}

function buildComparisonHtml(comp) {
  if (!comp || !comp.comparison_items || comp.comparison_items.length === 0) return "";
  const items = comp.comparison_items;

  const cardsHtml = items.map((p) => {
    const isBestVal = p.id === comp.best_value_id;
    const isTopRated = p.id === comp.highest_rated_id;
    return `
      <div class="comparison-item-card">
        <div class="comparison-badges">
          ${isBestVal ? `<span class="badge-winner-value">🏆 Best Value</span>` : ""}
          ${isTopRated ? `<span class="badge-winner-rating">⭐ Top Rated</span>` : ""}
          ${p.discount_pct ? `<span style="background: rgba(255,255,255,0.06); font-size: 10px; padding: 2px 6px; border-radius: 4px; color: #fff;">${p.discount_pct}% OFF</span>` : ""}
        </div>
        <img src="${p.image_url || '/static/images/honey.png'}" alt="${escapeHtml(p.name)}" onerror="this.src='/static/images/honey.png'">
        <div class="comp-prod-name">${escapeHtml(p.name)}</div>
        <div class="product-rating">
          <span class="star-icon">★</span>
          <span class="rating-score">${p.rating || 4.5}</span>
          <span class="review-count">(${p.review_count || 100} reviews)</span>
        </div>
        <div class="comp-price-row">
          <span class="comp-current-price">₹${Math.round(p.price).toLocaleString()}</span>
          ${p.mrp ? `<span class="comp-mrp">₹${Math.round(p.mrp).toLocaleString()}</span>` : ""}
        </div>
        <button class="btn-primary" style="margin-top: auto; padding: 8px 12px; font-size: 12px;" onclick="instantOrder(${p.id})">
          Order ${isBestVal ? "Best Value" : "This Model"}
        </button>
      </div>
    `;
  }).join("");

  return `
    <div class="comparison-card-wrapper">
      <div class="comparison-header-row">
        <div class="comparison-title">⚖️ Side-by-Side Product Comparison</div>
        <span style="font-size: 11px; color: var(--accent-gold); font-weight: 600;">Autonomous Matrix Analysis</span>
      </div>
      <div class="comparison-grid">
        ${cardsHtml}
      </div>
    </div>
  `;
}

function buildOrderTrackingHtml(ord) {
  if (!ord || !ord.found) return "";
  const steps = ord.checkpoints || [];

  const stepsHtml = steps.map((s) => `
    <div class="timeline-step ${s.completed ? 'completed' : ''}">
      <div class="timeline-step-dot"></div>
      <div class="timeline-step-info">
        <div class="timeline-step-title">${escapeHtml(s.status)}</div>
        <div class="timeline-step-sub">${escapeHtml(s.location)} • <span style="color: var(--accent-gold);">${escapeHtml(s.time)}</span></div>
      </div>
    </div>
  `).join("");

  return `
    <div class="order-tracking-card">
      <div class="tracking-card-header">
        <div>
          <div style="font-size: 14px; font-weight: 700; color: #fff;">📦 Order #${ord.order_id} — ${escapeHtml(ord.product_name)}</div>
          <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 2px;">Carrier: ${escapeHtml(ord.carrier)} • Tracking: <strong style="color: var(--accent-gold);">${escapeHtml(ord.tracking_number)}</strong></div>
        </div>
        <div class="tracking-pill">
          <span class="agent-pulse-dot" style="background:#48d585;"></span>
          <span>${escapeHtml(ord.current_status)}</span>
        </div>
      </div>
      <div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; font-size: 12px; color: #ded8cb;">
        <strong>Estimated Delivery:</strong> <span style="color: #48d585; font-weight: 600;">${escapeHtml(ord.estimated_delivery)}</span>
      </div>
      <div class="tracking-timeline">
        ${stepsHtml}
      </div>
    </div>
  `;
}

function buildCouponHtml(cpn) {
  if (!cpn || !cpn.valid) return "";
  return `
    <div style="background: linear-gradient(135deg, rgba(72, 213, 133, 0.12), rgba(245, 182, 101, 0.08)); border: 1px dashed #48d585; border-radius: 10px; padding: 12px 14px; margin: 10px 0;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 13px; font-weight: 700; color: #48d585;">🎟️ Coupon Applied: ${escapeHtml(cpn.code)}</span>
        <span style="background: rgba(72, 213, 133, 0.2); color: #48d585; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">Verified</span>
      </div>
      <div style="font-size: 12px; color: #ded8cb; margin-top: 4px;">${escapeHtml(cpn.savings_message)}</div>
    </div>
  `;
}

function renderAiResponse(data) {
  const row = document.createElement("div");
  row.className = "message-row ai-row";

  // Handle autonomous direct cart action if triggered by agent
  if (data.cart_action && data.cart_action.product) {
    const p = data.cart_action.product;
    addToCart(p.id, p.name, p.price, p.image);
  }

  const traceId = "trace_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
  const traceHtml = buildAgentTraceHtml(data.agent_trace, traceId);
  const compHtml = buildComparisonHtml(data.comparison);
  const trackHtml = buildOrderTrackingHtml(data.order_tracking);
  const couponHtml = buildCouponHtml(data.coupon);

  let productsHtml = "";
  if (data.products && data.products.length > 0 && !data.comparison) {
    const cards = data.products
      .map(
        (p) => `
        <div class="product-card" data-id="${p.id}" data-brand="${p.brand || ""}" data-rating="${p.rating || 4.5}" data-price="${p.price}">
          <div class="card-image-wrap">
            <img src="${p.image_url || '/static/images/honey.png'}" alt="${p.name}" class="card-img" onerror="this.src='/static/images/honey.png'">
            <button class="favorite-heart-btn ${state.wishlist.has(p.id) ? "active" : ""}" onclick="toggleWishlist(${p.id}, this)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
              </svg>
            </button>
          </div>
          <div class="card-content">
            <h3 class="product-name">${p.name}</h3>
            <div class="product-rating">
              <span class="star-icon">★</span>
              <span class="rating-score">${p.rating || 4.5}</span>
              <span class="review-count">(${p.review_count || 120} reviews)</span>
            </div>
            <div class="product-pricing">
              <span class="current-price">₹${Math.round(p.price).toLocaleString()}</span>
              ${p.mrp ? `<span class="mrp-price">₹${Math.round(p.mrp).toLocaleString()}</span>` : ""}
              ${p.discount_pct ? `<span class="discount-badge">${p.discount_pct}% OFF</span>` : ""}
            </div>
            <button class="view-details-btn" onclick="openProductModal(${p.id})">
              <span>View Details</span>
              <svg class="arrow-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>
      `
      )
      .join("");

    productsHtml = `
      <div class="product-cards-grid">
        ${cards}
      </div>
    `;
  }

  row.innerHTML = `
    <div class="avatar ai-avatar">
      <img src="/static/images/bazaar_emblem.jpg" alt="BazaarAi" class="avatar-emblem-img">
    </div>
    <div class="message-bubble-wrapper full-width">
      <div class="message-bubble ai-bubble">
        <div class="bubble-text">${formatMarkdown(data.content)}</div>
        <div class="message-timestamp-left">${data.timestamp || getCurrentTime()}</div>
      </div>
      ${traceHtml}
      ${compHtml}
      ${trackHtml}
      ${couponHtml}
      ${productsHtml}
    </div>
  `;

  dynamicMessagesContainer.appendChild(row);
}

// ==========================================================================
// QUICK FILTERS
// ==========================================================================

function applyQuickFilter(type, value) {
  state.activeFilters[type] = value;
  const cards = document.querySelectorAll(".product-cards-grid .product-card");

  cards.forEach((card) => {
    let show = true;
    const cardBrand = card.getAttribute("data-brand") || "";
    const cardRating = parseFloat(card.getAttribute("data-rating") || "0");
    const cardPrice = parseFloat(card.getAttribute("data-price") || "0");

    if (state.activeFilters.brand !== "all" && cardBrand.toLowerCase() !== state.activeFilters.brand.toLowerCase()) {
      show = false;
    }
    if (state.activeFilters.rating !== "all" && cardRating < parseFloat(state.activeFilters.rating)) {
      show = false;
    }
    if (state.activeFilters.price !== "all" && cardPrice > parseFloat(state.activeFilters.price)) {
      show = false;
    }

    card.style.display = show ? "flex" : "none";
  });

  showToast(`Applied ${type} filter: ${value}`);
}

// ==========================================================================
// PRODUCT DETAIL MODAL
// ==========================================================================

async function openProductModal(productId) {
  try {
    const res = await fetch(`/api/products/${productId}`);
    const prod = await res.json();

    const reviewsHtml = (prod.reviews || [])
      .slice(0, 3)
      .map(
        (r) => `
        <div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; margin-top: 6px;">
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #fff;">
            <strong>${escapeHtml(r.reviewer_name)}</strong>
            <span style="color: var(--accent-gold);">★ ${r.rating}</span>
          </div>
          <p style="font-size: 12px; color: #ccc; margin-top: 2px;">${escapeHtml(r.review_text)}</p>
        </div>
      `
      )
      .join("");

    productModalBody.innerHTML = `
      <div class="modal-product-detail">
        <img src="${prod.image_url || '/static/images/honey.png'}" alt="${prod.name}" class="modal-product-image">
        <div class="modal-product-info">
          <h2 class="modal-product-title">${prod.name}</h2>
          <div class="product-rating">
            <span class="star-icon">★</span>
            <span class="rating-score">${prod.rating || 4.5}</span>
            <span class="review-count">(${prod.review_count || 120} customer reviews)</span>
          </div>
          <div class="product-pricing">
            <span class="current-price" style="font-size: 22px;">₹${Math.round(prod.price).toLocaleString()}</span>
            ${prod.mrp ? `<span class="mrp-price" style="font-size: 15px;">₹${Math.round(prod.mrp).toLocaleString()}</span>` : ""}
            ${prod.discount_pct ? `<span class="discount-badge">${prod.discount_pct}% OFF</span>` : ""}
          </div>
          <p class="modal-product-desc">${prod.description || "High quality product carefully selected by BazaarAI."}</p>
          <div style="margin-top: 8px;">
            <strong style="font-size: 12.5px; color: var(--accent-gold);">Customer Reviews:</strong>
            ${reviewsHtml || "<div style='font-size: 12px; color: #888;'>No customer reviews yet.</div>"}
          </div>
          <div class="modal-btn-row">
            <button class="btn-secondary" onclick="addToCart(${prod.id}, '${escapeQuotes(prod.name)}', ${prod.price}, '${prod.image_url || '/static/images/honey.png'}')">
              Add to Cart
            </button>
            <button class="btn-primary" onclick="instantOrder(${prod.id})">
              Buy Now (1-Click)
            </button>
          </div>
        </div>
      </div>
    `;

    productModal.classList.add("open");
  } catch (e) {
    console.error(e);
    showToast("Error loading product details");
  }
}

function closeProductModal() {
  productModal.classList.remove("open");
}

async function instantOrder(productId) {
  try {
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId }),
    });
    const result = await res.json();
    closeProductModal();
    showToast(`🎉 ${result.message}`);
  } catch (e) {
    showToast("Failed to place order");
  }
}

// ==========================================================================
// CART DRAWER & WISHLIST
// ==========================================================================

function openCartDrawer() {
  updateCartUI();
  cartDrawer.classList.add("open");
}

function closeCartDrawer() {
  cartDrawer.classList.remove("open");
}

function addToCart(id, name, price, image) {
  const existing = state.cart.find((item) => item.id === id);
  if (existing) {
    existing.quantity += 1;
  } else {
    state.cart.push({ id, name, price, image, quantity: 1 });
  }
  updateCartUI();
  showToast(`Added ${name} to cart!`);
}

function removeFromCart(id) {
  state.cart = state.cart.filter((item) => item.id !== id);
  updateCartUI();
}

function updateCartUI() {
  const count = state.cart.reduce((sum, item) => sum + item.quantity, 0);
  cartBadgeCount.textContent = count;
  const countText = document.getElementById("cartItemCountText");
  if (countText) countText.textContent = count;

  let subtotal = 0;
  if (state.cart.length === 0) {
    cartItemsList.innerHTML = `<div style="text-align: center; color: #888; padding: 40px 0;">Your cart is empty.</div>`;
  } else {
    cartItemsList.innerHTML = state.cart
      .map((item) => {
        subtotal += item.price * item.quantity;
        return `
          <div class="cart-item">
            <img src="${item.image}" alt="${item.name}" class="cart-item-img">
            <div class="cart-item-details">
              <span class="cart-item-name">${item.name}</span>
              <span class="cart-item-price">₹${Math.round(item.price).toLocaleString()} × ${item.quantity}</span>
            </div>
            <button class="cart-item-remove" onclick="removeFromCart(${item.id})">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        `;
      })
      .join("");
  }

  const formattedTotal = `₹${Math.round(subtotal).toLocaleString()}`;
  cartSubtotalText.textContent = formattedTotal;
  cartTotalText.textContent = formattedTotal;
}

async function checkoutCart() {
  if (state.cart.length === 0) {
    showToast("Your cart is empty.");
    return;
  }
  for (const item of state.cart) {
    await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: item.id }),
    });
  }
  state.cart = [];
  updateCartUI();
  closeCartDrawer();
  showToast("🎉 Order placed for all cart items! Arriving in 2-3 business days.");
}

function toggleWishlist(id, btn) {
  if (state.wishlist.has(id)) {
    state.wishlist.delete(id);
    btn.classList.remove("active");
    showToast("Removed from Wishlist");
  } else {
    state.wishlist.add(id);
    btn.classList.add("active");
    showToast("Saved to Wishlist ❤️");
  }
}

// ==========================================================================
// SHOP BY IMAGE
// ==========================================================================

function openShopByImageModal() {
  shopByImageModal.classList.add("open");
}

function closeShopByImageModal() {
  shopByImageModal.classList.remove("open");
}

async function uploadAndSearchImage(file) {
  closeShopByImageModal();
  showToast("Uploading & analyzing product image…");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok || !data.filename) {
      throw new Error(data.detail || "Upload failed");
    }

    switchView("chat");
    handleSendMessage("Find products similar to this uploaded photo", {
      filename: data.filename,
      url: data.url,
      local_path: data.local_path,
    });
  } catch (e) {
    console.error("Upload error:", e);
    showToast("Failed to upload image");
  }
}

function selectSampleImage(filename, keyword) {
  closeShopByImageModal();
  switchView("chat");
  handleSendMessage(`Find ${keyword} similar to sample photo: ${filename}`, {
    filename: filename,
    url: `/static/images/${filename}`,
    local_path: `static/images/${filename}`,
  });
}

// ==========================================================================
// DATABASE & PRODUCTS MANAGER
// ==========================================================================

let cachedDbProducts = [];

async function openDatabaseModal() {
  const modal = document.getElementById("databaseModal");
  modal.classList.add("open");
  await fetchAndRenderDatabaseProducts();
}

function closeDatabaseModal() {
  document.getElementById("databaseModal").classList.remove("open");
}

async function fetchAndRenderDatabaseProducts() {
  try {
    const res = await fetch("/api/products");
    const data = await res.json();
    cachedDbProducts = data.products || [];
    renderDatabaseTable(cachedDbProducts);
  } catch (err) {
    showToast("Error loading database records");
  }
}

function renderDatabaseTable(products) {
  const tbody = document.getElementById("databaseTableBody");
  const countBadge = document.getElementById("dbProductCountBadge");
  if (countBadge) countBadge.textContent = `${products.length} products`;

  if (!products.length) {
    tbody.innerHTML = `<tr><td colspan="7" style="padding: 24px; text-align: center; color: #888;">No matching products found in database.</td></tr>`;
    return;
  }

  tbody.innerHTML = products
    .map(
      (p) => `
    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
      <td style="padding: 10px 14px; font-weight: 600; color: #ded9d1;">#${p.id}</td>
      <td style="padding: 10px 14px;">
        <img src="${p.image_url || "/static/images/honey.png"}" style="width: 38px; height: 38px; object-fit: cover; border-radius: 6px; background: #dfd6ca;" onerror="this.src='/static/images/honey.png'">
      </td>
      <td style="padding: 10px 14px; font-weight: 600; color: #fff;">${escapeHtml(p.name)}</td>
      <td style="padding: 10px 14px; color: var(--text-muted); text-transform: capitalize;">${escapeHtml(p.category || "general")}</td>
      <td style="padding: 10px 14px; font-weight: 700; color: var(--accent-gold);">₹${Math.round(p.price).toLocaleString()}</td>
      <td style="padding: 10px 14px; color: #fff;">★ ${p.rating || 4.5}</td>
      <td style="padding: 10px 14px; text-align: right;">
        <button onclick="deleteProduct(${p.id})" style="background: none; border: 1px solid rgba(255, 77, 79, 0.4); color: #ff6b6b; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11.5px;">Delete</button>
      </td>
    </tr>
  `
    )
    .join("");
}

function filterDatabaseTable() {
  const query = (document.getElementById("dbSearchInput")?.value || "").toLowerCase();
  const cat = document.getElementById("dbCategoryFilter")?.value || "all";

  const filtered = cachedDbProducts.filter((p) => {
    const matchName = (p.name || "").toLowerCase().includes(query) || (p.brand || "").toLowerCase().includes(query);
    const matchCat = cat === "all" || (p.category || "").toLowerCase() === cat.toLowerCase();
    return matchName && matchCat;
  });

  renderDatabaseTable(filtered);
}

function toggleAddProductForm() {
  const container = document.getElementById("addProductFormContainer");
  container.style.display = container.style.display === "none" ? "block" : "none";
}

async function submitNewProduct() {
  const name = document.getElementById("newProdName").value.trim();
  const category = document.getElementById("newProdCategory").value;
  const price = parseFloat(document.getElementById("newProdPrice").value);
  const mrp = parseFloat(document.getElementById("newProdMrp").value) || price;
  const brand = document.getElementById("newProdBrand").value.trim();
  const rating = parseFloat(document.getElementById("newProdRating").value) || 4.5;
  const image_url = document.getElementById("newProdImage").value.trim() || "/static/images/honey.png";
  const description = document.getElementById("newProdDesc").value.trim();

  if (!name || isNaN(price) || price <= 0) {
    showToast("Please enter a valid product name and price");
    return;
  }

  try {
    const res = await fetch("/api/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        category,
        price,
        mrp,
        brand,
        rating,
        image_url,
        description,
      }),
    });
    const result = await res.json();
    if (result.success) {
      showToast(`Added product "${name}" to store database!`);
      toggleAddProductForm();
      document.getElementById("newProdName").value = "";
      document.getElementById("newProdPrice").value = "";
      document.getElementById("newProdMrp").value = "";
      document.getElementById("newProdBrand").value = "";
      await fetchAndRenderDatabaseProducts();
    } else {
      showToast(result.message || "Failed to add product");
    }
  } catch (err) {
    showToast("Failed to connect to database");
  }
}

async function deleteProduct(id) {
  if (!confirm(`Are you sure you want to delete product #${id}?`)) return;

  try {
    const res = await fetch(`/api/products/${id}`, { method: "DELETE" });
    const result = await res.json();
    if (result.success) {
      showToast(`Product #${id} removed from database`);
      await fetchAndRenderDatabaseProducts();
    }
  } catch (err) {
    showToast("Error deleting product");
  }
}

// ==========================================================================
// ORDERS HISTORY
// ==========================================================================

async function openOrdersModal() {
  const modal = document.getElementById("ordersModal");
  modal.classList.add("open");
  try {
    const res = await fetch("/api/orders");
    const data = await res.json();
    const orders = data.orders || [];
    const tbody = document.getElementById("ordersTableBody");
    if (!orders.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="padding: 28px; text-align: center; color: #888;">No orders placed yet.</td></tr>`;
      return;
    }
    tbody.innerHTML = orders
      .map(
        (o) => `
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
        <td style="padding: 10px 14px; font-weight: 600; color: var(--accent-gold);">#${o.id}</td>
        <td style="padding: 10px 14px; font-weight: 600; color: #fff;">${escapeHtml(o.product_name)}</td>
        <td style="padding: 10px 14px; font-weight: 700; color: #fff;">₹${Math.round(o.price).toLocaleString()}</td>
        <td style="padding: 10px 14px; color: var(--text-muted);">${o.ordered_at || "Just now"}</td>
        <td style="padding: 10px 14px; text-align: right;">
          <span style="background: rgba(72, 213, 133, 0.15); color: #48d585; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">Confirmed</span>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    showToast("Error loading orders from database");
  }
}

function closeOrdersModal() {
  document.getElementById("ordersModal").classList.remove("open");
}

// ==========================================================================
// SETTINGS MODAL & COMMAND PALETTE
// ==========================================================================

function openSettingsModal() {
  settingsModal.classList.add("open");
  checkSettingsStatus();
}

function closeSettingsModal() {
  settingsModal.classList.remove("open");
}

async function checkSettingsStatus() {
  try {
    const res = await fetch("/api/settings");
    const data = await res.json();
    const statusMsg = document.getElementById("settingsSaveStatus");
    if (data.has_groq_key) {
      statusMsg.innerHTML = `<span style="color: #48d585;">● Groq API Key active (${data.masked_key})</span>`;
    } else {
      statusMsg.innerHTML = `<span style="color: #f5b665;">● Offline database mode active (enter Groq key for LLM)</span>`;
    }
  } catch (e) {}
}

async function saveSettings() {
  const keyInput = document.getElementById("groqApiKeyInput");
  const key = keyInput.value.trim();
  if (!key) {
    showToast("Please enter a valid key");
    return;
  }
  const res = await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ groq_api_key: key }),
  });
  const data = await res.json();
  if (data.success) {
    showToast("Groq API key saved successfully!");
    closeSettingsModal();
  }
}

function openSearchPalette() {
  searchPaletteModal.classList.add("open");
  loadPaletteSearchResults("");
  setTimeout(() => paletteSearchInput.focus(), 50);
}

function closeSearchPalette() {
  searchPaletteModal.classList.remove("open");
}

async function loadPaletteSearchResults(query) {
  const resultsContainer = document.getElementById("paletteResults");
  try {
    const res = await fetch(`/api/products?query=${encodeURIComponent(query)}`);
    const data = await res.json();
    const products = (data.products || []).slice(0, 5);

    let html = `<div class="palette-group-title">Products</div>`;
    if (products.length > 0) {
      html += products
        .map(
          (p) => `
        <div class="palette-item" onclick="closeSearchPalette(); startChatWithQuery('${escapeQuotes(p.name)}')">
          <span class="palette-item-icon">🛍️</span>
          <span>${escapeHtml(p.name)} — ₹${Math.round(p.price).toLocaleString()}</span>
        </div>
      `
        )
        .join("");
    } else {
      html += `<div style="padding: 8px 12px; color: #888; font-size: 12px;">No products match query.</div>`;
    }
    resultsContainer.innerHTML = html;
  } catch (e) {}
}

if (paletteSearchInput) {
  paletteSearchInput.addEventListener("input", (e) => {
    loadPaletteSearchResults(e.target.value);
  });
}

function closeAllModals() {
  productModal.classList.remove("open");
  cartDrawer.classList.remove("open");
  shopByImageModal.classList.remove("open");
  settingsModal.classList.remove("open");
  searchPaletteModal.classList.remove("open");
  const dbModal = document.getElementById("databaseModal");
  if (dbModal) dbModal.classList.remove("open");
  const ordModal = document.getElementById("ordersModal");
  if (ordModal) ordModal.classList.remove("open");
}

// ==========================================================================
// UTILITY HELPERS
// ==========================================================================

function getCurrentTime() {
  const d = new Date();
  let hours = d.getHours();
  const minutes = d.getMinutes().toString().padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  return `${hours}:${minutes} ${ampm}`;
}

function scrollToBottom() {
  setTimeout(() => {
    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: "smooth" });
  }, 100);
}

function showToast(message) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function escapeHtml(str) {
  return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeQuotes(str) {
  return (str || "").replace(/'/g, "\\'");
}

function formatMarkdown(text) {
  return (text || "")
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}
