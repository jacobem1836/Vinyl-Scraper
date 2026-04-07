/* ============================================================
   CRATE — Typeahead module
   Shared functions for Discogs search dropdown.
   Used in both add modal (index.html) and edit modal
   (index.html + item_detail.html).
   ============================================================ */

(function () {
  const DEBOUNCE_MS = 300;
  const MIN_QUERY_LEN = 2;

  // Types that activate the typeahead dropdown
  const ACTIVE_TYPES = ["album", "artist", "label"];

  // Per-prefix state map
  const state = {};

  /* ---------------------------------------------------------- */
  /* Internal helpers                                            */
  /* ---------------------------------------------------------- */

  function getEls(prefix) {
    return {
      input:   document.getElementById(prefix + "Query"),
      hidden:  document.getElementById(prefix + "DiscogsReleaseId"),
      spinner: document.getElementById(prefix + "Spinner"),
      listbox: document.getElementById(prefix + "-typeahead-listbox"),
    };
  }

  function closeDropdown(prefix) {
    const { input, listbox } = getEls(prefix);
    if (listbox) listbox.classList.remove("typeahead-dropdown--open");
    if (input) {
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
    }
    if (state[prefix]) state[prefix].activeIndex = -1;
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
        if (input) input.setAttribute("aria-activedescendant", row.id);
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

        // Thumbnail — use Discogs URL directly (no proxy needed for dropdown)
        const img = document.createElement("img");
        img.className = "typeahead-thumb";
        img.alt = "";
        img.src = result.thumb || "/static/vinyl-placeholder.svg";
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

        textDiv.appendChild(titleSpan);

        if (result.artist || result.year) {
          const year = result.year && result.year !== "0" ? result.year : null;
          const subtitle = result.artist + (year ? " \u00b7 " + year : "");
          const subtitleSpan = document.createElement("span");
          subtitleSpan.className = "text-sm text-muted";
          subtitleSpan.textContent = subtitle;
          textDiv.appendChild(subtitleSpan);
        }

        row.appendChild(img);
        row.appendChild(textDiv);

        row.addEventListener("click", function () {
          window.selectResult(prefix, result);
        });

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
    return ACTIVE_TYPES.includes(typeSelectEl.value);
  }

  /* ---------------------------------------------------------- */
  /* Public API                                                  */
  /* ---------------------------------------------------------- */

  /**
   * resetTypeahead — clear input, hidden value, and close dropdown.
   * Call when closing a modal to prevent stale state.
   */
  window.resetTypeahead = function (prefix) {
    const { input, hidden, spinner } = getEls(prefix);
    if (input) input.value = "";
    if (hidden) hidden.value = "";
    closeDropdown(prefix);
    if (spinner) spinner.classList.add("hidden");
  };

  /**
   * selectResult — fill the query input with the selected result.
   * For album type, also stores the release_id in the hidden input.
   * No locking — user can still edit the field freely.
   */
  window.selectResult = function (prefix, result) {
    const { input, hidden, spinner } = getEls(prefix);

    if (input) input.value = result.title;

    // Only store release_id for album selections (not artist/label)
    if (hidden) {
      hidden.value = result.release_id || "";
    }

    closeDropdown(prefix);
    if (spinner) spinner.classList.add("hidden");
    if (input) input.focus();
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

      const query = input.value.trim();
      if (query.length < MIN_QUERY_LEN || !isTypeaheadActive(typeSelectEl)) {
        closeDropdown(prefix);
        return;
      }

      const currentType = typeSelectEl ? typeSelectEl.value : "album";

      state[prefix].timer = setTimeout(function () {
        const ctrl = new AbortController();
        state[prefix].controller = ctrl;

        if (spinner) spinner.classList.remove("hidden");

        const url = "/api/discogs/search?q=" + encodeURIComponent(query) + "&type=" + encodeURIComponent(currentType);
        fetch(url, { signal: ctrl.signal })
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
            if (err.name === "AbortError") return;
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
        if (isOpen) {
          e.preventDefault(); // always prevent form submit while dropdown is open
          if (state[prefix].activeIndex >= 0) {
            const result = state[prefix].results[state[prefix].activeIndex];
            if (result) window.selectResult(prefix, result);
          } else if (state[prefix].results.length > 0) {
            // No item highlighted — select the first result
            window.selectResult(prefix, state[prefix].results[0]);
          }
        }
      } else if (e.key === "Escape") {
        closeDropdown(prefix);
      } else if (e.key === "Tab") {
        closeDropdown(prefix);
      }
    });

    // Close dropdown and clear release_id when type changes
    if (typeSelectEl) {
      typeSelectEl.addEventListener("change", function () {
        closeDropdown(prefix);
        // Clear stored release_id — it's type-specific
        const { hidden, spinner } = getEls(prefix);
        if (hidden) hidden.value = "";
        if (spinner) spinner.classList.add("hidden");
      });
    }
  };
})();
