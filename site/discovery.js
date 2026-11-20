/* PickRepo discovery: static, browser-only search, filters, images and transparent fit score. */
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
  const guideSummaries = catalog.guideSummaries || {};
  const media = catalog.media || {};
  const DAY = 24 * 60 * 60 * 1000;
  const DEFAULT_WEIGHTS = { relevance: 30, activity: 25, community: 20, recency: 15, context: 10 };
  const FACTORS = [
    { key: "relevance", input: "weightRelevance", output: "weightOutRelevance", labelId: "weightLabelRelevance" },
    { key: "activity", input: "weightActivity", output: "weightOutActivity", labelId: "weightLabelActivity" },
    { key: "community", input: "weightCommunity", output: "weightOutCommunity", labelId: "weightLabelCommunity" },
    { key: "recency", input: "weightRecency", output: "weightOutRecency", labelId: "weightLabelRecency" },
    { key: "context", input: "weightContext", output: "weightOutContext", labelId: "weightLabelContext" }
  ];

  const TEXT = {
    tr: {
      localeLabel: "Dil",
      heroEyebrow: "Açık kaynak dünyasına yeni bir bakış",
      heroBrowse: "Projeleri keşfet",
      heroNote: "Her gün yenilenir · Ücretsiz · Hesap gerekmez",
      heroStatCollections: "Keşif listesi",
      heroStatRepositories: "Açık repo",
      heroStatGuides: "Kaynaklı rehber",
      views: { trending: "Yükselenler", popular: "Popüler", early: "Erken keşif", guides: "Kaynaklı rehberler" },
      viewDescriptions: {
        trending: "Son 7 günde oluşturulan herkese açık depolar; toplam yıldız sayısına göre sıralanır. Haftalık yıldız artışı ölçülmez.",
        popular: "En az 1.000 yıldızlı herkese açık depolar. Yıldız sayısı tek başına kalite göstergesi değildir.",
        early: "Son 30 günde oluşturulmuş, 10–1.000 yıldız aralığındaki yeni depolar.",
        guides: "PickRepo’nun Türkçe ve İngilizce kaynaklı rehber hazırladığı projeler."
      },
      searchLabel: "Proje ara",
      searchPlaceholder: "Ad, açıklama veya GitHub konusu",
      languageLabel: "Programlama dili",
      allLanguages: "Tüm diller",
      topicLabel: "GitHub konusu",
      allTopics: "Tüm konular",
      sortLabel: "Sıralama",
      sortMatch: "PickRepo keşif puanı",
      sortStars: "En çok yıldız",
      sortUpdated: "Son güncellenen",
      sortCreated: "En yeni oluşturulan",
      scoreSummary: "Keşif puanını kişiselleştir · nasıl hesaplanıyor?",
      scoreIntro: "Ağırlıkları değiştirince sıralama bu tarayıcıda yenilenir. Yüzdeler otomatik olarak 100’e tamamlanır; tercihler kaydedilmez.",
      weightLabels: {
        relevance: "Arama ve konu uyumu",
        activity: "Yakın tarihli güncelleme",
        community: "Yıldız ve fork topluluğu",
        recency: "Projenin yeniliği",
        context: "Proje bilgilerinin doluluğu"
      },
      weightNote: "Ağırlıklar otomatik olarak 100’e tamamlanır.",
      resetWeights: "Varsayılan ağırlıkları geri yükle",
      scoreMethod: "Bu puan bir keşif yardımcısıdır; kalite veya güvenlik garantisi değildir. PickRepo repo kodunu çalıştırmaz. Tarihsel yıldız kayıtları olmadığı için son hafta kazanılan yıldız sayısı ölçülmez. Lisans etiketi hukuki lisans değerlendirmesi değildir. Hesap, e-posta uyarısı veya sunucu gerekmez.",
      empty: "Bu filtrelerde sonuç bulunamadı. Arama sözcüğünü veya filtreleri değiştirebilirsiniz.",
      resultCount: (count) => count + " proje",
      unspecified: "Belirtilmemiş",
      noLicense: "GitHub’da belirtilmemiş",
      scoreLabel: "PickRepo keşif puanı",
      sourceDescription: "GitHub açıklaması · özgün dil",
      noDescription: "GitHub açıklaması eklenmemiş; ayrıntılar için kaynak depoyu inceleyin.",
      detailsSummary: "Ayrıntılar · Nedir? Ne işe yarar? Nasıl kurulur?",
      whatTitle: "Nedir?",
      useTitle: "Ne işe yarar?",
      installTitle: "Nasıl kurulur?",
      fallbackWhat: "Bu proje için PickRepo tarafından hazırlanmış iki dilli kısa açıklama henüz yok. Proje sahibinin özgün açıklaması aşağıda gösteriliyor.",
      fallbackUse: "Kullanım amacını proje sahibinin README’sinden inceleyin. PickRepo bu repo için ayrıca bir kullanım testi yapmadı.",
      fallbackInstall: "Kurulum adımları proje sahibinin resmî README’sindedir. Bu sitede kurulum denenmedi; komutları çalıştırmadan önce kaynağı inceleyin.",
      officialReadme: "README / resmî kaynak ↗",
      guideLink: "Kaynaklı rehber ↗",
      screenshotCaption: "Resmî depo görseli",
      illustrationCaption: "Temsili illüstrasyon · ekran görüntüsü değil",
      artLabel: "için temsili illüstrasyon",
      facts: { created: "Oluşturulma", updated: "Son değişiklik", stars: "Toplam yıldız", forks: "Fork", license: "Lisans", topics: "GitHub konuları" },
      factorLabels: { relevance: "Arama ve konu uyumu", activity: "Yakın tarihli güncelleme", community: "Yıldız ve fork topluluğu", recency: "Projenin yeniliği", context: "Proje bilgilerinin doluluğu" },
      methodNote: "Bu keşif puanı GitHub metaverilerinden türetilen bir sıralama yardımcısıdır; kodu çalıştırmaz, güvenliği veya kaliteyi doğrulamaz. Tarihsel yıldız kayıtları tutulmadığından yıldız kazanma hızı puanlanmaz. Lisans etiketi hukuki lisans değerlendirmesi değildir.",
      navDiscover: "Keşfet",
      navGuides: "Rehberler",
      sidebarDiscover: "↗ Projeleri keşfet",
      sidebarGuides: "▤ Kaynaklı rehberler",
      footerNote: "GitHub ile bağlantılı olmayan bağımsız bir keşif aracı.",
      footerSponsor: "Sponsor olun",
      footerPrivacy: "Gizlilik",
      footerTerms: "Kullanım koşulları"
    },
    en: {
      localeLabel: "Language",
      heroEyebrow: "A fresh lens on open source",
      heroBrowse: "Explore projects",
      heroNote: "Updated daily · Free · No account",
      heroStatCollections: "Discovery lists",
      heroStatRepositories: "Public repositories",
      heroStatGuides: "Source-based guides",
      views: { trending: "Trending", popular: "Popular", early: "Early finds", guides: "Source-based guides" },
      viewDescriptions: {
        trending: "Public repositories created in the last 7 days, sorted by total stars. Weekly star growth is not measured.",
        popular: "Public repositories with at least 1,000 stars. Star count alone is not a quality signal.",
        early: "New repositories created in the last 30 days with 10–1,000 stars.",
        guides: "Projects with detailed, bilingual, source-based PickRepo guides."
      },
      searchLabel: "Search projects",
      searchPlaceholder: "Name, description, or GitHub topic",
      languageLabel: "Programming language",
      allLanguages: "All languages",
      topicLabel: "GitHub topic",
      allTopics: "All topics",
      sortLabel: "Sort by",
      sortMatch: "PickRepo discovery score",
      sortStars: "Most stars",
      sortUpdated: "Recently updated",
      sortCreated: "Newest repositories",
      scoreSummary: "Personalize the discovery score · how it works",
      scoreIntro: "Changing weights reorders results in this browser. Weights are normalized to 100%; preferences are not saved.",
      weightLabels: {
        relevance: "Search and topic match",
        activity: "Recent repository update",
        community: "Stars and forks",
        recency: "Repository age",
        context: "Repository information completeness"
      },
      weightNote: "Weights are automatically normalized to 100%.",
      resetWeights: "Restore default weights",
      scoreMethod: "This is a discovery aid, not a quality or security guarantee. PickRepo does not run repository code. Historical star snapshots are not stored, so recent star growth is not measured. The license label is not legal advice. No account, email alerts, or server is required.",
      empty: "No projects match these filters. Try changing the search term or filters.",
      resultCount: (count) => count + (count === 1 ? " project" : " projects"),
      unspecified: "Unspecified",
      noLicense: "Not specified on GitHub",
      scoreLabel: "PickRepo discovery score",
      sourceDescription: "GitHub description · original language",
      noDescription: "No GitHub description is provided. Open the source repository for details.",
      detailsSummary: "Details · What is it? What is it for? How do I install it?",
      whatTitle: "What is it?",
      useTitle: "What is it useful for?",
      installTitle: "How do I install it?",
      fallbackWhat: "A short, bilingual PickRepo summary is not available for this project yet. The project owner’s original description is shown below.",
      fallbackUse: "Check the owner’s README for the intended use. PickRepo has not independently tested this repository.",
      fallbackInstall: "Follow the project owner’s official README. Installation was not tested on this site; review commands before running them.",
      officialReadme: "README / official source ↗",
      guideLink: "Source-based guide ↗",
      screenshotCaption: "Official repository image",
      illustrationCaption: "Illustrative artwork · not a screenshot",
      artLabel: "illustrative artwork for",
      facts: { created: "Created", updated: "Last update", stars: "Total stars", forks: "Forks", license: "License", topics: "GitHub topics" },
      factorLabels: { relevance: "Search and topic match", activity: "Recent repository update", community: "Stars and forks", recency: "Repository age", context: "Repository information completeness" },
      methodNote: "This discovery score is a ranking aid based on GitHub metadata; it does not run code or verify quality or security. Historical star snapshots are not stored, so star velocity is not scored. License labels are not legal advice.",
      navDiscover: "Discover",
      navGuides: "Guides",
      sidebarDiscover: "↗ Discover projects",
      sidebarGuides: "▤ Source-based guides",
      footerNote: "An independent discovery tool, not affiliated with GitHub.",
      footerSponsor: "Sponsors",
      footerPrivacy: "Privacy",
      footerTerms: "Terms"
    }
  };

  const VIEW_META = {
    trending: { title: { tr: "Yükselenler", en: "Trending" } },
    popular: { title: { tr: "Popüler", en: "Popular" } },
    early: { title: { tr: "Erken keşif", en: "Early finds" } },
    guides: { title: { tr: "Kaynaklı rehberler", en: "Source-based guides" } }
  };
  const VIEW_DESCRIPTIONS = {
    trending: { tr: TEXT.tr.viewDescriptions.trending, en: TEXT.en.viewDescriptions.trending },
    popular: { tr: TEXT.tr.viewDescriptions.popular, en: TEXT.en.viewDescriptions.popular },
    early: { tr: TEXT.tr.viewDescriptions.early, en: TEXT.en.viewDescriptions.early },
    guides: { tr: TEXT.tr.viewDescriptions.guides, en: TEXT.en.viewDescriptions.guides }
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
  const localeButtons = Array.from(document.querySelectorAll("[data-locale]"));
  let activeView = "trending";

  const browserLanguage = typeof navigator !== "undefined" ? String(navigator.language || "").toLowerCase() : "tr";
  let activeLocale = browserLanguage.startsWith("en") ? "en" : "tr";
  const allRepositories = Object.values(repos);
  const maxStars = Math.max(0, ...allRepositories.map((repo) => Number(repo.stargazers_count) || 0));
  const maxForks = Math.max(0, ...allRepositories.map((repo) => Number(repo.forks_count) || 0));
  const maxLogStars = Math.log1p(maxStars) || 1;
  const maxLogForks = Math.log1p(maxForks) || 1;

  function text() {
    return TEXT[activeLocale] || TEXT.tr;
  }

  function escapeHTML(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[char]);
  }

  function displayLanguage(repo) {
    return repo.language || text().unspecified;
  }

  function languageValue(repo) {
    return repo.language || "__unspecified__";
  }

  function readableLicense(repo) {
    const value = repo.license;
    if (!value || value === "NOASSERTION") return text().noLicense;
    return value;
  }

  function parseDate(value) {
    const date = value ? new Date(value) : null;
    return date && Number.isFinite(date.getTime()) ? date : null;
  }

  function formatDate(value) {
    const date = parseDate(value);
    if (!date) return text().unspecified;
    return new Intl.DateTimeFormat(activeLocale === "en" ? "en-GB" : "tr-TR", {
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
    if (repo.language) score += 15;
    if (topics.length > 0) score += Math.min(25, 10 + topics.length * 5);
    if (repo.license && repo.license !== "NOASSERTION") score += 25;
    return Math.min(100, score);
  }

  function tokenize(value) {
    return String(value || "")
      .toLocaleLowerCase(activeLocale === "en" ? "en-GB" : "tr-TR")
      .split(/[^\p{L}\p{N}+#.-]+/u)
      .filter((part) => part.length > 1);
  }

  function relevanceScore(repo, query) {
    const topicNames = Array.isArray(repo.topics) ? repo.topics : [];
    const q = tokenize(query);
    if (!q.length) return 50;
    const locale = activeLocale === "en" ? "en-GB" : "tr-TR";
    const fields = [
      { text: String(repo.full_name || "").toLocaleLowerCase(locale), weight: 1.3 },
      { text: topicNames.join(" ").toLocaleLowerCase(locale), weight: 1.2 },
      { text: String(repo.description || "").toLocaleLowerCase(locale), weight: 1.0 },
      { text: String(repo.language || "").toLocaleLowerCase(locale), weight: 0.5 }
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
    const score = FACTORS.reduce((sum, factor) => sum + factors[factor.key] * weights[factor.key], 0) / totalWeight;
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
    const languages = Array.from(new Set(current.map(languageValue))).sort((a, b) => a.localeCompare(b, "en"));
    const topics = new Map();
    current.forEach((repo) => {
      (Array.isArray(repo.topics) ? repo.topics : []).forEach((topic) => topics.set(topic, (topics.get(topic) || 0) + 1));
    });

    if (languageSelect) {
      const previous = languageSelect.value;
      languageSelect.innerHTML = '<option value="all">' + escapeHTML(text().allLanguages) + '</option>' + languages.map((language) => {
        const label = language === "__unspecified__" ? text().unspecified : language;
        return '<option value="' + escapeHTML(language) + '">' + escapeHTML(label) + '</option>';
      }).join("");
      if (languages.includes(previous)) languageSelect.value = previous;
    }

    if (topicSelect) {
      const previous = topicSelect.value;
      const sortedTopics = Array.from(topics.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 60);
      topicSelect.innerHTML = '<option value="all">' + escapeHTML(text().allTopics) + '</option>' + sortedTopics.map(([topic, count]) => {
        return '<option value="' + escapeHTML(topic) + '">' + escapeHTML(topic) + ' · ' + count + '</option>';
      }).join("");
      if (sortedTopics.some(([topic]) => topic === previous)) topicSelect.value = previous;
    }
  }

  function scoreMarkup(value, label) {
    const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
    return '<div class="signal-row"><div class="signal-heading"><span>' + escapeHTML(label) + '</span><span>' + safeValue + '/100</span></div>' +
      '<div class="signal-track" role="img" aria-label="' + escapeHTML(label) + ': ' + safeValue + ' / 100"><span style="width:' + safeValue + '%"></span></div></div>';
  }

  function starsMarkup(repo) {
    const stars = Number(repo.stargazers_count) || 0;
    return '<span class="star"><span class="star-icon" aria-hidden="true">★</span> ' + stars.toLocaleString(activeLocale === "en" ? "en-US" : "tr-TR") + '</span>';
  }

  function hashHue(value) {
    let hash = 0;
    for (let i = 0; i < value.length; i += 1) hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
    return hash % 360;
  }

  function visualMarkup(repo) {
    const fullName = String(repo.full_name || "");
    const image = media[fullName.toLowerCase()];
    const t = text();
    if (image && typeof image.path === "string" && image.path.startsWith("/assets/repo-media/")) {
      const alt = image.alt || (fullName + " project image");
      const sourceURL = image.source || ("https://github.com/" + fullName + "#readme");
      return '<figure class="project-visual"><img src="' + escapeHTML(image.path) + '" alt="' + escapeHTML(alt) + '" loading="lazy" decoding="async"><figcaption>' + escapeHTML(t.screenshotCaption) + ' · <a href="' + escapeHTML(sourceURL) + '" target="_blank" rel="noopener noreferrer">' + escapeHTML(activeLocale === "en" ? "source" : "kaynağı") + ' ↗</a></figcaption></figure>';
    }
    const name = fullName.split("/").pop() || fullName;
    const initials = name.slice(0, 2).toUpperCase();
    const hue = hashHue(fullName);
    const language = repo.language || t.unspecified;
    return '<figure class="project-visual"><div class="project-visual-art" style="--visual-hue:' + hue + '" role="img" aria-label="' + escapeHTML(fullName + " " + t.artLabel) + '">' +
      '<div class="art-orbit" aria-hidden="true"></div><div class="art-window" aria-hidden="true"><div class="art-window-bar"><i></i><i></i><i></i></div>' +
      '<div class="art-window-content"><span class="art-glyph">' + escapeHTML(initials) + '</span><span class="art-lines"><i></i><i></i><i></i></span></div></div>' +
      '<div class="art-caption"><strong>' + escapeHTML(name) + '</strong><span>' + escapeHTML(language) + '</span></div></div><figcaption>' + escapeHTML(t.illustrationCaption) + '</figcaption></figure>';
  }

  function cardMarkup(repo, index, searchQuery) {
    const t = text();
    const fullName = String(repo.full_name || "");
    const parts = fullName.split("/");
    const owner = parts[0] || "";
    const name = parts.slice(1).join("/") || fullName;
    const githubURL = "https://github.com/" + fullName;
    const description = String(repo.description || "").trim();
    const displayDescription = description || t.noDescription;
    const topics = Array.isArray(repo.topics) ? repo.topics : [];
    const license = readableLicense(repo);
    const language = displayLanguage(repo);
    const result = scoreRepo(repo, searchQuery);
    const repoKey = fullName.toLowerCase();
    const guideSlug = guideSlugs[repoKey];
    const guideSummary = guideSummaries[repoKey] && guideSummaries[repoKey][activeLocale];
    const whatText = guideSummary && guideSummary.what ? guideSummary.what : t.fallbackWhat;
    const useText = guideSummary && guideSummary.use ? guideSummary.use : t.fallbackUse;
    const installText = guideSummary && guideSummary.install ? guideSummary.install : t.fallbackInstall;
    const guideAction = guideSlug ? '<a class="btn guide-btn" href="/guide/' + escapeHTML(guideSlug) + '.html">' + escapeHTML(t.guideLink) + '</a>' : "";
    const topicTags = topics.slice(0, 6).map((topic) => '<span class="topic-chip">' + escapeHTML(topic) + '</span>').join("");
    const factorsHTML = FACTORS.map((factor) => scoreMarkup(result.factors[factor.key], t.factorLabels[factor.key])).join("");
    const starCount = Number(repo.stargazers_count) || 0;
    const forkCount = Number(repo.forks_count) || 0;
    const created = formatDate(repo.created_at);
    const updated = formatDate(repo.pushed_at);
    const topicText = topics.length ? topics.join(", ") : t.unspecified;
    const guideInstallNote = guideSummary ? " <a class=\"inline-guide-link\" href=\"/guide/" + escapeHTML(guideSlug) + ".html\">" + escapeHTML(t.guideLink) + "</a>" : "";

    return '<article class="project-card">' +
      '<div class="project-card-top"><span class="rank-number" aria-label="' + escapeHTML((activeLocale === "en" ? "Rank " : "Sıra ") + (index + 1)) + '">' + (index + 1) + '</span>' +
      '<div class="project-title-wrap"><h2 class="project-title"><a href="' + escapeHTML(githubURL) + '" target="_blank" rel="noopener noreferrer">' + escapeHTML(owner) + ' / <strong>' + escapeHTML(name) + '</strong></a></h2></div>' +
      '<div class="project-score"><span>' + escapeHTML(t.scoreLabel) + '</span><strong>' + result.score + '<small>/100</small></strong></div></div>' +
      '<div class="project-card-content">' + visualMarkup(repo) + '<div class="project-summary">' +
      '<span class="source-description-label">' + escapeHTML(t.sourceDescription) + '</span><p class="project-description">' + escapeHTML(displayDescription) + '</p>' +
      (topicTags ? '<div class="topic-list" aria-label="' + escapeHTML(t.facts.topics) + '">' + topicTags + '</div>' : '') +
      '<div class="project-meta">' + starsMarkup(repo) + '<span>' + escapeHTML(language) + '</span><span>' + escapeHTML(t.facts.forks) + ' ' + forkCount.toLocaleString(activeLocale === "en" ? "en-US" : "tr-TR") + '</span><span>' + escapeHTML(t.facts.license) + ': ' + escapeHTML(license) + '</span></div></div></div>' +
      '<details class="project-details"><summary>' + escapeHTML(t.detailsSummary) + '</summary><div class="details-body">' +
      '<div class="localized-explainer"><section><h3>' + escapeHTML(t.whatTitle) + '</h3><p>' + escapeHTML(whatText) + '</p></section>' +
      '<section><h3>' + escapeHTML(t.useTitle) + '</h3><p>' + escapeHTML(useText) + '</p></section>' +
      '<section><h3>' + escapeHTML(t.installTitle) + '</h3><p>' + escapeHTML(installText) + guideInstallNote + '</p></section></div>' +
      '<span class="source-description-label">' + escapeHTML(t.sourceDescription) + '</span><p class="detail-lead">' + escapeHTML(displayDescription) + '</p>' +
      '<div class="detail-facts"><div><strong>' + escapeHTML(t.facts.created) + '</strong><span>' + escapeHTML(created) + '</span></div>' +
      '<div><strong>' + escapeHTML(t.facts.updated) + '</strong><span>' + escapeHTML(updated) + '</span></div>' +
      '<div><strong>' + escapeHTML(t.facts.stars) + '</strong><span>' + starCount.toLocaleString(activeLocale === "en" ? "en-US" : "tr-TR") + '</span></div>' +
      '<div><strong>' + escapeHTML(t.facts.forks) + '</strong><span>' + forkCount.toLocaleString(activeLocale === "en" ? "en-US" : "tr-TR") + '</span></div>' +
      '<div><strong>' + escapeHTML(t.facts.license) + '</strong><span>' + escapeHTML(license) + '</span></div>' +
      '<div><strong>' + escapeHTML(t.facts.topics) + '</strong><span>' + escapeHTML(topicText) + '</span></div></div>' +
      '<h3>' + escapeHTML(activeLocale === "en" ? "Discovery signals" : "Keşif sinyalleri") + '</h3><div class="signal-grid">' + factorsHTML + '</div>' +
      '<p class="method-note">' + escapeHTML(t.methodNote) + '</p>' +
      '<div class="detail-actions"><a href="' + escapeHTML(githubURL) + '#readme" target="_blank" rel="noopener noreferrer">' + escapeHTML(t.officialReadme) + '</a>' + guideAction + '</div></div></details>' +
      '<div class="project-actions">' + guideAction + '<a class="btn" href="' + escapeHTML(githubURL) + '" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>' +
      '</article>';
  }

  function sponsorMarkup() {
    const t = text();
    return '<div class="sponsor sponsor-slot"><div><strong>' + escapeHTML(activeLocale === "en" ? "Sponsor space" : "Sponsor alanı") + '</strong><p>' + escapeHTML(activeLocale === "en" ? "No active sponsor." : "Henüz aktif sponsor yok.") + '</p></div><a class="btn" href="/sponsor.html">' + escapeHTML(t.footerSponsor) + ' ↗</a></div>';
  }

  function updateWeightsUI() {
    let rawTotal = FACTORS.reduce((sum, factor) => {
      const input = document.getElementById(factor.input);
      return sum + (input ? Math.max(0, Number(input.value) || 0) : DEFAULT_WEIGHTS[factor.key]);
    }, 0);
    if (!rawTotal) FACTORS.forEach((factor) => {
      const input = document.getElementById(factor.input);
      if (input) input.value = 20;
    });
    const values = readWeights();
    const total = Object.values(values).reduce((sum, value) => sum + value, 0) || 1;
    FACTORS.forEach((factor) => {
      const output = document.getElementById(factor.output);
      const label = document.getElementById(factor.labelId);
      if (output) output.textContent = Math.round((values[factor.key] / total) * 100) + "%";
      if (label) label.textContent = text().weightLabels[factor.key];
    });
    if (weightTotalNode) weightTotalNode.textContent = text().weightNote;
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
      if (selectedLanguage !== "all" && languageValue(repo) !== selectedLanguage) return false;
      if (selectedTopic !== "all" && !topics.includes(selectedTopic)) return false;
      if (tokens.length) {
        const searchable = [repo.full_name, repo.description, repo.language, repo.license, ...topics]
          .filter(Boolean).join(" ").toLocaleLowerCase(activeLocale === "en" ? "en-GB" : "tr-TR");
        if (!tokens.every((token) => searchable.includes(token))) return false;
      }
      return true;
    });

    const sortMode = sortSelect ? sortSelect.value : "stars";
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
    if (countNode) countNode.textContent = text().resultCount(filtered.length);
    if (emptyNode) {
      emptyNode.hidden = filtered.length > 0;
      emptyNode.textContent = text().empty;
    }
  }

  function applyLocale() {
    const t = text();
    if (document.documentElement) document.documentElement.lang = activeLocale;
    const ids = {
      localeLabel: t.localeLabel,
      heroEyebrow: t.heroEyebrow,
      heroBrowse: t.heroBrowse,
      heroNote: t.heroNote,
      heroStatCollections: t.heroStatCollections,
      heroStatRepositories: t.heroStatRepositories,
      heroStatGuides: t.heroStatGuides,
      searchLabel: t.searchLabel,
      languageLabel: t.languageLabel,
      topicLabel: t.topicLabel,
      sortLabel: t.sortLabel,
      scoreSummary: t.scoreSummary,
      scoreIntro: t.scoreIntro,
      resetWeights: t.resetWeights,
      scoreMethod: t.scoreMethod,
      navDiscover: t.navDiscover,
      navGuides: t.navGuides,
      sidebarTitle: t.navDiscover,
      sidebarDiscover: t.sidebarDiscover,
      sidebarGuides: t.sidebarGuides,
      footerNote: t.footerNote,
      footerSponsor: t.footerSponsor,
      footerPrivacy: t.footerPrivacy,
      footerTerms: t.footerTerms,
      sortMatch: t.sortMatch,
      sortStars: t.sortStars,
      sortUpdated: t.sortUpdated,
      sortCreated: t.sortCreated
    };
    Object.entries(ids).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
    if (searchInput) searchInput.placeholder = t.searchPlaceholder;
    localeButtons.forEach((button) => {
      const active = button.dataset.locale === activeLocale;
      button.classList.toggle("current", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    viewButtons.forEach((button) => button.textContent = t.views[button.dataset.view] || button.dataset.view);
    const meta = VIEW_META[activeView];
    if (titleNode && meta) titleNode.textContent = meta.title[activeLocale];
    if (descriptionNode) descriptionNode.textContent = VIEW_DESCRIPTIONS[activeView][activeLocale];
    refreshFilterOptions();
    updateWeightsUI();
    render();
  }

  function setView(view) {
    if (!VIEW_META[view]) return;
    activeView = view;
    const meta = VIEW_META[view];
    if (titleNode) titleNode.textContent = meta.title[activeLocale];
    if (descriptionNode) descriptionNode.textContent = VIEW_DESCRIPTIONS[view][activeLocale];
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
  localeButtons.forEach((button) => button.addEventListener("click", () => {
    activeLocale = button.dataset.locale === "en" ? "en" : "tr";
    applyLocale();
  }));
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

  applyLocale();
})();
