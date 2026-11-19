/* PickRepo discovery: static, browser-only search, filters and transparent fit score. */
(function () {
  "use strict";

  const dataNode = document.getElementById("catalogData");
  if (!dataNode) return;

  let catalog;
  try {
    catalog = JSON.parse(dataNode.textContent || "{}");
  } catch (error) {
    console.error("PickRepo catalog could not be read.", error);
    return;
  }

  const repos = catalog.repos || {};
  const views = catalog.views || {};
  const guideSlugs = catalog.guideSlugs || {};
  const DAY = 24 * 60 * 60 * 1000;
  const DEFAULT_WEIGHTS = {
    relevance: 30,
    activity: 25,
    community: 20,
    recency: 15,
    context: 10
  };
  const FACTORS = [
    { key: "relevance", label: "Arama ve konu uyumu", input: "weightRelevance", output: "weightOutRelevance" },
    { key: "activity", label: "Yakın tarihli güncelleme", input: "weightActivity", output: "weightOutActivity" },
    { key: "community", label: "Yıldız ve fork topluluğu", input: "weightCommunity", output: "weightOutCommunity" },
    { key: "recency", label: "Projenin yeniliği", input: "weightRecency", output: "weightOutRecency" },
    { key: "context", label: "Proje bilgilerinin doluluğu", input: "weightContext", output: "weightOutContext" }
  ];
  const VIEW_META = {
    trending: {
      title: "Yükselenler",
      description: "Son 7 günde oluşturulan herkese açık depolar; toplam yıldız sayısına göre sıralanır. Haftalık yıldız artışı ölçülmez."
    },
    popular: {
      title: "Popüler",
      description: "En az 1.000 yıldızlı herkese açık depolar. Yıldız sayısı tek başına kalite göstergesi değildir."
    },
    early: {
      title: "Erken keşif",
      description: "Son 30 günde oluşturulmuş, 10–1.000 yıldız aralığındaki yeni depolar."
    },
    guides: {
      title: "Kaynaklı rehberler",
      description: "PickRepo’nun Türkçe ve İngilizce kaynaklı rehber hazırladığı projeler."
    }
  };

  const list = document.getElementById("repoList");
  const searchInput = document.getElementById("searchInput");
  const languageSelect = document.getElementById("langSelect");
  const topicSelect = document.getElementById("topicSelect");
  const sortSelect = document.getElementById("sortSelect");
  const countNode = document.getElementById("resultCount");
  const emptyNode = document.getElementById("emptyState");
  const titleNode = document.getElementById("pageTitle");
  const descriptionNode = document.getElementById("pageDescription");
  const weightTotalNode = document.getElementById("weightTotal");
  const viewButtons = Array.from(document.querySelectorAll("[data-view]"));
  let activeView = "trending";

  const allRepositories = Object.values(repos);
  const maxStars = Math.max(0, ...allRepositories.map((repo) => Number(repo.stargazers_count) || 0));
  const maxForks = Math.max(0, ...allRepositories.map((repo) => Number(repo.forks_count) || 0));
  const maxLogStars = Math.log1p(maxStars) || 1;
  const maxLogForks = Math.log1p(maxForks) || 1;

  function escapeHTML(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[char]);
  }

  function readableLanguage(repo) {
    return repo.language || "Belirtilmemiş";
  }

  function readableLicense(repo) {
    const value = repo.license;
    if (!value || value === "NOASSERTION") return "GitHub’da belirtilmemiş";
    return value;
  }

  function parseDate(value) {
    const date = value ? new Date(value) : null;
    return date && Number.isFinite(date.getTime()) ? date : null;
  }

  function formatDate(value) {
    const date = parseDate(value);
    if (!date) return "Belirtilmemiş";
    return new Intl.DateTimeFormat("tr-TR", {
      year: "numeric",
      month: "short",
      day: "numeric",
      timeZone: "UTC"
    }).format(date);
  }

  function ageInDays(value) {
    const date = parseDate(value);
    if (!date) return null;
    return Math.max(0, (Date.now() - date.getTime()) / DAY);
  }

  function activityScore(repo) {
    const age = ageInDays(repo.pushed_at);
    if (age == null) return 20;
    if (age <= 7) return 100;
    if (age <= 30) return 88;
    if (age <= 90) return 70;
    if (age <= 180) return 52;
    if (age <= 365) return 34;
    return 15;
  }

  function recencyScore(repo) {
    const age = ageInDays(repo.created_at);
    if (age == null) return 20;
    if (age <= 7) return 100;
    if (age <= 30) return 88;
    if (age <= 90) return 72;
    if (age <= 365) return 55;
    if (age <= 1095) return 38;
    return 22;
  }

  function communityScore(repo) {
    const stars = Number(repo.stargazers_count) || 0;
    const forks = Number(repo.forks_count) || 0;
    const starPart = Math.log1p(stars) / maxLogStars;
    const forkPart = Math.log1p(forks) / maxLogForks;
    return Math.round((starPart * 0.8 + forkPart * 0.2) * 100);
  }

  function contextScore(repo) {
    const description = String(repo.description || "").trim();
    const topics = Array.isArray(repo.topics) ? repo.topics : [];
    let score = 0;
    if (description.length >= 40) score += 35;
    else if (description.length > 0) score += 20;
    if (readableLanguage(repo) !== "Belirtilmemiş") score += 15;
    if (topics.length > 0) score += Math.min(25, 10 + topics.length * 5);
    if (repo.license && repo.license !== "NOASSERTION") score += 25;
    return Math.min(100, score);
  }

  function tokenize(value) {
    return String(value || "")
      .toLocaleLowerCase("tr-TR")
      .split(/[^\p{L}\p{N}+#.-]+/u)
      .filter((part) => part.length > 1);
  }

  function relevanceScore(repo, query) {
    const topicNames = Array.isArray(repo.topics) ? repo.topics : [];
    const q = tokenize(query);
    if (!q.length) return 50;

    const ownerAndName = String(repo.full_name || "").toLocaleLowerCase("tr-TR");
    const description = String(repo.description || "").toLocaleLowerCase("tr-TR");
    const topics = topicNames.join(" ").toLocaleLowerCase("tr-TR");
    const language = String(repo.language || "").toLocaleLowerCase("tr-TR");
    const fields = [
      { text: ownerAndName, weight: 1.3 },
      { text: topics, weight: 1.2 },
      { text: description, weight: 1.0 },
      { text: language, weight: 0.5 }
    ];
    let total = 0;
    q.forEach((word) => {
      let best = 0;
      fields.forEach((field) => {
        if (field.text.includes(word)) best = Math.max(best, field.weight);
      });
      total += best / 1.3;
    });
    return Math.round((total / q.length) * 100);
  }

  function readWeights() {
    const values = {};
    FACTORS.forEach((factor) => {
      const input = document.getElementById(factor.input);
      values[factor.key] = input ? Math.max(0, Number(input.value) || 0) : DEFAULT_WEIGHTS[factor.key];
    });
    const total = Object.values(values).reduce((sum, value) => sum + value, 0);
    if (!total) return { ...DEFAULT_WEIGHTS };
    return values;
  }

  function scoreRepo(repo, query) {
    const weights = readWeights();
    const totalWeight = Object.values(weights).reduce((sum, value) => sum + value, 0) || 1;
    const factors = {
      relevance: relevanceScore(repo, query),
      activity: activityScore(repo),
      community: communityScore(repo),
      recency: recencyScore(repo),
      context: contextScore(repo)
    };
    const score = FACTORS.reduce((sum, factor) => {
      return sum + factors[factor.key] * weights[factor.key];
    }, 0) / totalWeight;
    return { score: Math.round(score), factors };
  }

  function viewNames(view) {
    if (view === "guides") return Object.keys(guideSlugs);
    return Array.isArray(views[view]) ? views[view] : [];
  }

  function repoFor(name) {
    const key = String(name || "").toLowerCase();
    return repos[key] || allRepositories.find((repo) => String(repo.full_name || "").toLowerCase() === key) || null;
  }

  function getCurrentRepos() {
    return viewNames(activeView).map(repoFor).filter(Boolean);
  }

  function refreshFilterOptions() {
    const current = getCurrentRepos();
    const languages = Array.from(new Set(current.map(readableLanguage))).sort((a, b) => a.localeCompare(b, "tr"));
    const topics = new Map();
    current.forEach((repo) => {
      (Array.isArray(repo.topics) ? repo.topics : []).forEach((topic) => {
        topics.set(topic, (topics.get(topic) || 0) + 1);
      });
    });

    if (languageSelect) {
      const previous = languageSelect.value;
      languageSelect.innerHTML = '<option value="all">Tüm diller</option>' + languages.map((language) => {
        return '<option value="' + escapeHTML(language) + '">' + escapeHTML(language) + '</option>';
      }).join("");
      if (languages.includes(previous)) languageSelect.value = previous;
    }

    if (topicSelect) {
      const previous = topicSelect.value;
      const sortedTopics = Array.from(topics.entries())
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .slice(0, 60);
      topicSelect.innerHTML = '<option value="all">Tüm konular</option>' + sortedTopics.map(([topic, count]) => {
        return '<option value="' + escapeHTML(topic) + '">' + escapeHTML(topic) + ' · ' + count + '</option>';
      }).join("");
      if (sortedTopics.some(([topic]) => topic === previous)) topicSelect.value = previous;
    }
  }

  function scoreMarkup(value, label) {
    const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
    return '<div class="signal-row"><div class="signal-heading"><span>' + escapeHTML(label) + '</span><span>' + safeValue + '/100</span></div>' +
      '<div class="signal-track" role="img" aria-label="' + escapeHTML(label) + ': ' + safeValue + ' üzerinden 100"><span style="width:' + safeValue + '%"></span></div></div>';
  }

  function starsMarkup(repo) {
    const stars = Number(repo.stargazers_count) || 0;
    return '<span class="star"><span class="star-icon" aria-hidden="true">★</span> ' + stars.toLocaleString("tr-TR") + '</span>';
  }

  function cardMarkup(repo, index, searchQuery) {
    const fullName = String(repo.full_name || "");
    const parts = fullName.split("/");
    const owner = parts[0] || "";
    const name = parts.slice(1).join("/") || fullName;
    const githubURL = "https://github.com/" + fullName;
    const description = String(repo.description || "").trim();
    const topics = Array.isArray(repo.topics) ? repo.topics : [];
    const license = readableLicense(repo);
    const language = readableLanguage(repo);
    const result = scoreRepo(repo, searchQuery);
    const guideSlug = guideSlugs[fullName.toLowerCase()];
    const guideAction = guideSlug ? '<a class="btn guide-btn" href="/guide/' + escapeHTML(guideSlug) + '.html">Kaynaklı rehber ↗</a>' : "";
    const topicTags = topics.slice(0, 6).map((topic) => '<span class="topic-chip">' + escapeHTML(topic) + '</span>').join("");
    const factorsHTML = FACTORS.map((factor) => scoreMarkup(result.factors[factor.key], factor.label)).join("");
    const starCount = Number(repo.stargazers_count) || 0;
    const forkCount = Number(repo.forks_count) || 0;
    const created = formatDate(repo.created_at);
    const updated = formatDate(repo.pushed_at);
    const safeDescription = description ? escapeHTML(description) : "GitHub açıklaması eklenmemiş; ayrıntılar için kaynak depoyu inceleyin.";
    const topicText = topics.length ? topics.join(", ") : "Belirtilmemiş";

    return '<article class="project-card" data-language="' + escapeHTML(language) + '">' +
      '<div class="project-card-top"><span class="rank-number">' + (index + 1) + '.</span>' +
      '<div class="project-title-wrap"><span class="project-kicker">GitHub projesi</span>' +
      '<h2 class="project-title"><a href="' + escapeHTML(githubURL) + '" target="_blank" rel="noopener noreferrer">' + escapeHTML(owner) + ' / <strong>' + escapeHTML(name) + '</strong></a></h2></div>' +
      '<div class="project-score"><span>PickRepo keşif puanı</span><strong>' + result.score + '<small>/100</small></strong></div></div>' +
      '<p class="project-description">' + safeDescription + '</p>' +
      (topicTags ? '<div class="topic-list" aria-label="GitHub konuları">' + topicTags + '</div>' : '') +
      '<div class="project-meta">' + starsMarkup(repo) +
      '<span>' + escapeHTML(language) + '</span><span>Fork ' + forkCount.toLocaleString("tr-TR") + '</span>' +
      '<span>Lisans: ' + escapeHTML(license) + '</span><span>Son değişiklik: ' + escapeHTML(updated) + '</span></div>' +
      '<details class="project-details"><summary>Ayrıntılar · bu puan neye dayanıyor?</summary>' +
      '<div class="details-body"><p class="detail-lead">' + safeDescription + '</p>' +
      '<div class="detail-facts"><div><strong>Oluşturulma</strong><span>' + escapeHTML(created) + '</span></div>' +
      '<div><strong>Son değişiklik</strong><span>' + escapeHTML(updated) + '</span></div>' +
      '<div><strong>Toplam yıldız</strong><span>' + starCount.toLocaleString("tr-TR") + '</span></div>' +
      '<div><strong>Fork</strong><span>' + forkCount.toLocaleString("tr-TR") + '</span></div>' +
      '<div><strong>Lisans</strong><span>' + escapeHTML(license) + '</span></div>' +
      '<div><strong>GitHub konuları</strong><span>' + escapeHTML(topicText) + '</span></div></div>' +
      '<h3>Keşif sinyalleri</h3><div class="signal-grid">' + factorsHTML + '</div>' +
      '<p class="method-note">Bu keşif puanı GitHub metaverilerinden türetilen bir sıralama yardımcısıdır; kodu çalıştırmaz, güvenliği veya kaliteyi doğrulamaz. Tarihsel yıldız kayıtları tutulmadığından yıldız kazanma hızı puanlanmaz. Lisans bilgisi de kullanım izninin hukuki değerlendirmesi değildir.</p>' +
      '<div class="detail-actions"><a href="' + escapeHTML(githubURL) + '#readme" target="_blank" rel="noopener noreferrer">README / kaynak ↗</a>' + guideAction + '</div></div></details>' +
      '<div class="project-actions">' + guideAction + '<a class="btn" href="' + escapeHTML(githubURL) + '" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>' +
      '</article>';
  }

  function sponsorMarkup() {
    return '<div class="sponsor sponsor-slot"><div><strong>Sponsor alanı</strong><p>Henüz aktif sponsor yok.</p></div><a class="btn" href="/sponsor.html">Sponsor ol ↗</a></div>';
  }

  function updateWeightsUI() {
    let rawTotal = FACTORS.reduce((sum, factor) => {
      const input = document.getElementById(factor.input);
      return sum + (input ? Math.max(0, Number(input.value) || 0) : DEFAULT_WEIGHTS[factor.key]);
    }, 0);
    if (!rawTotal) {
      FACTORS.forEach((factor) => {
        const input = document.getElementById(factor.input);
        if (input) input.value = 20;
      });
    }
    const values = readWeights();
    const total = Object.values(values).reduce((sum, value) => sum + value, 0) || 1;
    FACTORS.forEach((factor) => {
      const output = document.getElementById(factor.output);
      if (output) output.textContent = Math.round((values[factor.key] / total) * 100) + "%";
    });
    if (weightTotalNode) weightTotalNode.textContent = "Ağırlıklar otomatik olarak 100’e tamamlanır.";
  }

  function render() {
    if (!list) return;
    const query = searchInput ? searchInput.value.trim() : "";
    const tokens = tokenize(query);
    const selectedLanguage = languageSelect ? languageSelect.value : "all";
    const selectedTopic = topicSelect ? topicSelect.value : "all";
    const current = getCurrentRepos();
    const filtered = current.filter((repo) => {
      const topics = Array.isArray(repo.topics) ? repo.topics : [];
      if (selectedLanguage !== "all" && readableLanguage(repo) !== selectedLanguage) return false;
      if (selectedTopic !== "all" && !topics.includes(selectedTopic)) return false;
      if (tokens.length) {
        const searchable = [repo.full_name, repo.description, repo.language, repo.license, ...topics]
          .filter(Boolean).join(" ").toLocaleLowerCase("tr-TR");
        if (!tokens.every((token) => searchable.includes(token))) return false;
      }
      return true;
    });

    const sortMode = sortSelect ? sortSelect.value : "match";
    const scored = filtered.map((repo) => ({ repo, result: scoreRepo(repo, query) }));
    scored.sort((a, b) => {
      if (sortMode === "stars") return (Number(b.repo.stargazers_count) || 0) - (Number(a.repo.stargazers_count) || 0);
      if (sortMode === "updated") return (parseDate(b.repo.pushed_at)?.getTime() || 0) - (parseDate(a.repo.pushed_at)?.getTime() || 0);
      if (sortMode === "created") return (parseDate(b.repo.created_at)?.getTime() || 0) - (parseDate(a.repo.created_at)?.getTime() || 0);
      return b.result.score - a.result.score || (Number(b.repo.stargazers_count) || 0) - (Number(a.repo.stargazers_count) || 0);
    });

    const rendered = [];
    scored.forEach((item, index) => {
      rendered.push(cardMarkup(item.repo, index, query));
      if ([3, 6, 9].includes(index + 1)) rendered.push(sponsorMarkup());
    });
    list.innerHTML = rendered.join("");
    if (countNode) countNode.textContent = filtered.length + (filtered.length === 1 ? " proje" : " proje");
    if (emptyNode) emptyNode.hidden = filtered.length > 0;
  }

  function setView(view) {
    if (!VIEW_META[view]) return;
    activeView = view;
    const meta = VIEW_META[view];
    if (titleNode) titleNode.textContent = meta.title;
    if (descriptionNode) descriptionNode.textContent = meta.description;
    viewButtons.forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle("current", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    if (languageSelect) languageSelect.value = "all";
    if (topicSelect) topicSelect.value = "all";
    refreshFilterOptions();
    render();
  }

  viewButtons.forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  [searchInput, languageSelect, topicSelect, sortSelect].forEach((control) => {
    if (control) control.addEventListener(control === searchInput ? "input" : "change", render);
  });
  FACTORS.forEach((factor) => {
    const input = document.getElementById(factor.input);
    if (input) input.addEventListener("input", () => {
      updateWeightsUI();
      render();
    });
  });
  const resetButton = document.getElementById("resetWeights");
  if (resetButton) resetButton.addEventListener("click", () => {
    FACTORS.forEach((factor) => {
      const input = document.getElementById(factor.input);
      if (input) input.value = DEFAULT_WEIGHTS[factor.key];
    });
    updateWeightsUI();
    render();
  });

  refreshFilterOptions();
  updateWeightsUI();
  render();
})();
