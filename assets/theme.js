(function () {
  const THEME_KEY = "fastone-hermes-theme";
  const LOGO_ASSETS = {
    light: {
      full: "./public/assets/logo/fastone-logo-light.png",
      mark: "./public/assets/logo/fastone-logo-light.png",
    },
    dark: {
      full: "./public/assets/logo/fastone-logo-dark.png",
      mark: "./public/assets/logo/fastone-logo-dark.png",
    },
  };

  function systemTheme() {
    try {
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    } catch {
      return "dark";
    }
  }

  function pageDefaultTheme() {
    return (
      document.documentElement.getAttribute("data-theme-default")
      || document.body?.getAttribute("data-theme-default")
      || ""
    ).trim();
  }

  function resolveTheme() {
    try {
      const saved = localStorage.getItem(THEME_KEY);
      if (saved === "light" || saved === "dark") return saved;
    } catch {}
    const preferred = pageDefaultTheme();
    if (preferred === "light" || preferred === "dark") return preferred;
    return systemTheme();
  }

  function themedLogoPath(kind, theme) {
    const mode = theme === "light" ? "light" : "dark";
    const key = kind === "mark" ? "mark" : "full";
    return LOGO_ASSETS[mode][key];
  }

  function applyThemedLogos(theme) {
    document.querySelectorAll("[data-themed-logo]").forEach((img) => {
      if (!img || img.tagName !== "IMG") return;
      const kind = (img.getAttribute("data-themed-logo") || "full").trim().toLowerCase();
      img.setAttribute("src", themedLogoPath(kind, theme));
    });
  }

  function applyTheme(theme, options = {}) {
    const nextTheme = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nextTheme);
    if (document.body) document.body.setAttribute("data-theme", nextTheme);
    applyThemedLogos(nextTheme);
    document.querySelectorAll("[data-theme-toggle-mode]").forEach((button) => {
      const active = button.getAttribute("data-theme-toggle-mode") === nextTheme;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      const target = nextTheme === "dark" ? "light" : "dark";
      button.setAttribute("data-theme-next", target);
      button.setAttribute("aria-label", target === "dark" ? "切换到深色主题" : "切换到浅色主题");
      button.textContent = nextTheme === "dark" ? "浅色" : "深色";
    });
    if (options.persist === false) return nextTheme;
    try {
      localStorage.setItem(THEME_KEY, nextTheme);
    } catch {}
    return nextTheme;
  }

  function bindThemeControls(root = document) {
    root.querySelectorAll("[data-theme-toggle-mode]").forEach((button) => {
      if (button.dataset.themeBound === "1") return;
      button.dataset.themeBound = "1";
      button.addEventListener("click", () => {
        applyTheme(button.getAttribute("data-theme-toggle-mode") || "dark");
      });
    });
    root.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      if (button.dataset.themeBound === "1") return;
      button.dataset.themeBound = "1";
      button.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
        applyTheme(current === "dark" ? "light" : "dark");
      });
    });
  }

  function initTheme() {
    applyTheme(resolveTheme(), { persist: false });
    bindThemeControls();
  }

  window.FastoneTheme = {
    key: THEME_KEY,
    resolveTheme,
    applyTheme,
    bindThemeControls,
    initTheme,
  };

  initTheme();
})();
