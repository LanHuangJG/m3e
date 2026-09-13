window.addEventListener("DOMContentLoaded", () => {
  M3eDirectionality.observe(() => {
    const frame = document.querySelector("#content-frame");
    frame.contentWindow.postMessage(
      { type: "direction-change", dir: M3eDirectionality.current },
      window.location.origin,
    );
  });

  const frame = document.querySelector("#content-frame");
  frame.addEventListener("load", () => {
    const scheme = document.querySelector("m3e-theme").scheme;
    switch (document.querySelector("m3e-theme").scheme) {
      case "light":
      case "dark":
        frame.contentDocument.documentElement.style.colorScheme = scheme;
        break;
    }

    const currentUrl = frame.contentWindow?.location.href.substring(document.baseURI.length);
    history.replaceState({}, "", "#/" + currentUrl);

    const menuItem = document.querySelector(`a[href='${currentUrl}']`)?.closest("m3e-nav-menu-item");
    if (menuItem) {
      menuItem.selected = true;
    }
    selectPanel(groupForPath(currentUrl), false);
    frame.removeAttribute("hidden");
  });

  // Only allow "[segment/]*file.html" paths, no suspicious characters
  const allowedPathRegex = /^([a-zA-Z0-9_-]+\/)*[a-zA-Z0-9_-]+\.html$/;
  const requestedPath = location.hash ? location.hash.substring(2) : "";
  const initialPath = allowedPathRegex.test(requestedPath) ? requestedPath : "getting-started/overview.html";
  frame.src = initialPath;

  const rail = document.querySelector("#rail");
  const flyout = document.querySelector("#flyout");
  const menuButton = document.querySelector("#menu-button");
  const railItems = rail ? [...rail.querySelectorAll("m3e-nav-item")] : [];

  function groupForPath(path) {
    const segment = (path || "").split("/")[0];
    return ["getting-started", "styles", "frameworks", "components"].includes(segment) ? segment : "getting-started";
  }

  function selectPanel(key, open = true) {
    if (!flyout) {
      return;
    }
    for (const panel of flyout.querySelectorAll("[data-panel]")) {
      panel.hidden = panel.dataset.panel !== key;
    }
    for (const item of railItems) {
      const selected = item.dataset.panel === key;
      if (item.selected !== selected) {
        item.selected = selected;
      }
    }
    if (open) {
      flyout.hidden = false;
      if (menuButton) {
        menuButton.selected = true;
      }
    }
  }

  rail?.addEventListener("change", () => {
    const item = railItems.find((x) => x.selected);
    if (item) {
      selectPanel(item.dataset.panel);
    }
  });

  menuButton?.addEventListener("change", () => {
    if (flyout) {
      flyout.hidden = !menuButton.selected;
    }
  });

  flyout?.addEventListener("click", (e) => {
    if (!e.target.closest("a[href]")) {
      return;
    }
    if (window.matchMedia("(max-width: 900px)").matches) {
      flyout.hidden = true;
      if (menuButton) {
        menuButton.selected = false;
      }
    }
  });

  selectPanel(groupForPath(initialPath), true);

  const color = document.querySelector("#color");
  if (color) {
    color.value = document.querySelector("m3e-theme").color;
    color.addEventListener("change", () => {
      document.querySelector("m3e-theme").color = color.value;
      frame.contentWindow.postMessage({ type: "color-change", color: color.value }, window.location.origin);
    });
  }

  const colorSchemeButton = document.querySelector("#color-scheme-button");
  if (colorSchemeButton) {
    colorSchemeButton.addEventListener("change", () => {
      const theme = document.querySelector("m3e-theme");

      const frame = document.querySelector("#content-frame");
      switch (colorSchemeButton.value) {
        case "light":
        case "dark":
          document.documentElement.style.colorScheme = frame.contentDocument.documentElement.style.colorScheme =
            colorSchemeButton.value;
          break;
        default:
          document.documentElement.style.colorScheme = frame.contentDocument.documentElement.style.colorScheme = "";
          break;
      }
      theme.scheme = colorSchemeButton.value;
      frame.contentWindow.postMessage({ type: "color-scheme-change", scheme: theme.scheme }, window.location.origin);
    });
  }

  const contrastButton = document.querySelector("#contrast-button");
  if (contrastButton) {
    contrastButton.addEventListener("change", () => {
      const theme = document.querySelector("m3e-theme");
      theme.contrast = contrastButton.value;
      frame.contentWindow.postMessage({ type: "contrast-change", contrast: theme.contrast }, window.location.origin);
    });
  }

  const directionalityButton = document.querySelector("#directionality-button");
  if (directionalityButton) {
    directionalityButton.addEventListener("change", () => {
      document.documentElement.dir = directionalityButton.value;
    });
  }

  const textSizeButton = document.querySelector("#text-size-button");
  if (textSizeButton) {
    textSizeButton.addEventListener("change", () => {
      document.documentElement.style.fontSize = textSizeButton.value;
      frame.contentWindow.postMessage(
        { type: "text-size-change", textSize: textSizeButton.value },
        window.location.origin,
      );
    });
  }
});
