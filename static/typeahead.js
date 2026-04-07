/* ============================================================
   CRATE — Typeahead module
   Shared functions for Discogs release search dropdown.
   Used in both add modal (index.html) and edit modal
   (index.html + item_detail.html).
   ============================================================ */

(function () {
  const DEBOUNCE_MS = 300;
  const MIN_QUERY_LEN = 2;

  // Per-prefix state map
  const state = {};

  /* ---------------------------------------------------------- */
  /* Internal helpers                                            */
  /* ---------------------------------------------------------- */

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function getEls(prefix) {
    return {
      input:    document.getElementById(prefix + "Query"),
      badge:    document.getElementById(prefix + "PinBadge"),
      pinText:  document.getElementById(prefix + "PinText"),
      hidden:   document.getElementById(prefix + "DiscogsReleaseId"),
      spinner:  document.getElementById(prefix + "Spinner"),
      listbox:  document.getElementById(prefix + "-typeahead-listbox"),
    };
  }

  function closeDropdown(prefix) {
    const { input, listbox } = getEls(prefix);
    if (listbox) {
      listbox.classList.remove("typeahead-dropdown--open");
    }
    if (input) {
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
    }
    if (state[prefix]) {
      state[prefix].activeIndex = -1;
    }
  }

  function updateActiveRow(prefix) {
    const { listbox, input } = getEls(prefix);
    if (!listbox) return;
    const rows = listbox.querySelectorAll(".typeahead-row");
    const idx = state[prefix].activeIndex;
    rows.forEach((row, i) => {
      if (i === idx) {
        row.classList.add("typeahead-row--active");
        row.setAttribute("aria-selected", "true");
        input && input.setAttribute("aria-activedescendant", row.id);
      } else {
        row.classList.remove("typeahead-row--active");
        row.setAttribute("aria-selected", "false");
      }
    });
  }

  function renderResults(prefix, results, query) {
    const { listbox } = getEls(prefix);
    if (!listbox) return;

    listbox.innerHTML = "";
    state[prefix].results = results;

    if (!results || results.length === 0) {
      const empty = document.createElement("div");
      empty.className = "typeahead-empty";
      empty.textContent = "No results for \u201c" + query + "\u201d";
      listbox.appendChild(empty);
    } else {
      results.forEach(function (result, i) {
        const row = document.createElement("div");
        row.className = "typeahead-row";
        row.setAttribute("role", "option");
        row.setAttribute("id", prefix + "-option-" + i);
        row.setAttribute("aria-selected", "false");
        row.setAttribute("data-index", i);

        // Thumbnail
        const img = document.createElement("img");
        img.className = "typeahead-thumb";
        img.alt = "";
        if (result.thumb) {
          img.src = "/api/artwork?url=" + encodeURIComponent(result.thumb);
        } else {
          img.src = "/static/vinyl-placeholder.svg";
        }
        img.onerror = function () { this.src = "/static/vinyl-placeholder.svg"; };

        // Text block
        const textDiv = document.createElement("div");
        textDiv.style.display = "flex";
        textDiv.style.flexDirection = "column";
        textDiv.style.gap = "2px";
        textDiv.style.overflow = "hidden";

        const titleSpan = document.createElement("span");
        titleSpan.className = "text-sm";
        titleSpan.style.color = "var(--color-text)";
        titleSpan.textContent = result.title;

        const year = result.year && result.year !== "0" ? result.year : null;
        const subtitle = result.artist + (year ? " \u00b7 " + year : "");
        const subtitleSpan = document.createElement("span");
        subtitleSpan.className = "text-sm text-muted";
        subtitleSpan.textContent = subtitle;

        textDiv.appendChild(titleSpan);
        textDiv.appendChild(subtitleSpan);

        row.appendChild(img);
        row.appendChild(textDiv);

        // Click handler
        row.addEventListener("click", function () {
          window.selectResult(prefix, result);
        });

        // Mouseover handler — update active index visually
        row.addEventListener("mouseover", function () {
          state[prefix].activeIndex = i;
          updateActiveRow(prefix);
        });

        listbox.appendChild(row);
      });
    }

    listbox.classList.add("typeahead-dropdown--open");
    const { input } = getEls(prefix);
    if (input) input.setAttribute("aria-expanded", "true");
  }

  function isTypeaheadActive(typeSelectEl) {
    if (!typeSelectEl) return false;
    const val = typeSelectEl.value;
    return val === "album" || val === "subject";
  }

  /* ---------------------------------------------------------- */
  /* Public API                                                  */
  /* ---------------------------------------------------------- */

  /**
   * selectResult — called on click or Enter key press.
   * Sets hidden input, locks query field, shows pin badge.
   */
  window.selectResult = function (prefix, result) {
    const { input, badge, pinText, hidden } = getEls(prefix);

    // Set hidden release ID
    if (hidden) hidden.value = result.release_id;

    // Fill and lock query input
    if (input) {
      input.value = result.title;
      input.classList.add("form-input--locked");
      input.readOnly = true;
      input.placeholder = "Release pinned \u2014 clear badge to change";
      input.title = "Clear the pinned release above to edit this field";
    }

    // Show pin badge
    const year = result.year && result.year !== "0" ? result.year : null;
    if (pinText) pinText.textContent = result.title + (year ? " (" + year + ")" : "");
    if (badge) badge.classList.remove("hidden");

    // Close dropdown
    closeDropdown(prefix);
  };

  /**
   * clearPin — clears pinned release, unlocks query input.
   */
  window.clearPin = function (prefix) {
    const { input, badge, hidden } = getEls(prefix);

    if (hidden) hidden.value = "";
    if (input) {
      input.classList.remove("form-input--locked");
      input.readOnly = false;
      input.placeholder = "Search Discogs...";
      input.removeAttribute("title");
      input.value = "";
      input.focus();
    }
    if (badge) badge.classList.add("hidden");

    closeDropdown(prefix);
  };

  /**
   * setPin — pre-populate badge for edit modal (D-04).
   * Does NOT set query input value — caller handles that.
   */
  window.setPin = function (prefix, releaseId, displayText) {
    const { input, badge, pinText, hidden } = getEls(prefix);

    if (hidden) hidden.value = releaseId;
    if (input) {
      input.classList.add("form-input--locked");
      input.readOnly = true;
      input.placeholder = "Release pinned \u2014 clear badge to change";
      input.title = "Clear the pinned release above to edit this field";
    }
    if (pinText) pinText.textContent = displayText;
    if (badge) badge.classList.remove("hidden");
  };

  /**
   * initTypeahead — initialize typeahead for a given prefix.
   * prefix: 'add' or 'edit'
   * typeSelectEl: the <select name="type"> element for this modal
   */
  window.initTypeahead = function (prefix, typeSelectEl) {
    state[prefix] = {
      timer: null,
      controller: null,
      activeIndex: -1,
      results: [],
    };

    const { input, spinner } = getEls(prefix);
    if (!input) return;

    // Input event — debounced fetch
    input.addEventListener("input", function () {
      if (state[prefix].timer) clearTimeout(state[prefix].timer);
      if (state[prefix].controller) {
        try { state[prefix].controller.abort(); } catch (e) {}
      }

      if (input.readOnly) return;

      const query = input.value.trim();
      if (query.length < MIN_QUERY_LEN || !isTypeaheadActive(typeSelectEl)) {
        closeDropdown(prefix);
        return;
      }

      state[prefix].timer = setTimeout(function () {
        const ctrl = new AbortController();
        state[prefix].controller = ctrl;

        if (spinner) spinner.classList.remove("hidden");

        fetch("/api/discogs/search?q=" + encodeURIComponent(query), { signal: ctrl.signal })
          .then(function (res) {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
          })
          .then(function (data) {
            if (spinner) spinner.classList.add("hidden");
            renderResults(prefix, data, query);
          })
          .catch(function (err) {
            if (spinner) spinner.classList.add("hidden");
            if (err.name === "AbortError") return; // expected — rapid typing
            // Network/server error
            const { listbox } = getEls(prefix);
            if (listbox) {
              listbox.innerHTML = "";
              const errDiv = document.createElement("div");
              errDiv.className = "typeahead-empty";
              errDiv.textContent = "Search unavailable. Try again.";
              listbox.appendChild(errDiv);
              listbox.classList.add("typeahead-dropdown--open");
              input.setAttribute("aria-expanded", "true");
            }
          });
      }, DEBOUNCE_MS);
    });

    // Keyboard navigation
    input.addEventListener("keydown", function (e) {
      const { listbox } = getEls(prefix);
      const isOpen = listbox && listbox.classList.contains("typeahead-dropdown--open");
      const rows = listbox ? listbox.querySelectorAll(".typeahead-row") : [];

      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (!isOpen || rows.length === 0) return;
        state[prefix].activeIndex = (state[prefix].activeIndex + 1) % rows.length;
        updateActiveRow(prefix);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (!isOpen || rows.length === 0) return;
        state[prefix].activeIndex =
          state[prefix].activeIndex <= 0
            ? rows.length - 1
            : state[prefix].activeIndex - 1;
        updateActiveRow(prefix);
      } else if (e.key === "Enter") {
        if (isOpen && state[prefix].activeIndex >= 0) {
          e.preventDefault();
          const result = state[prefix].results[state[prefix].activeIndex];
          if (result) window.selectResult(prefix, result);
        }
      } else if (e.key === "Escape") {
        closeDropdown(prefix);
      } else if (e.key === "Tab") {
        closeDropdown(prefix);
      }
    });

    // Type select change — disable typeahead for artist/label
    if (typeSelectEl) {
      typeSelectEl.addEventListener("change", function () {
        if (!isTypeaheadActive(typeSelectEl)) {
          closeDropdown(prefix);
          // Do NOT clear the pin if one exists — just close dropdown
        }
      });
    }
  };
})();
