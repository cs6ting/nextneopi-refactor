(() => {
  "use strict";

  const search = document.getElementById("api-search");
  const items = Array.from(document.querySelectorAll("[data-nav-item]"));
  const groups = Array.from(document.querySelectorAll(".nav-group"));

  if (search) {
    search.addEventListener("input", () => {
      const query = search.value.trim().toLowerCase();
      items.forEach((item) => {
        item.hidden = Boolean(query) && !item.dataset.search.includes(query);
      });
      groups.forEach((group) => {
        const visible = Array.from(group.querySelectorAll("[data-nav-item]")).some(
          (item) => !item.hidden
        );
        group.hidden = !visible;
      });
    });
  }

  document.querySelectorAll("pre").forEach((pre) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-code";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "复制代码");

    const selectCode = () => {
      const range = document.createRange();
      range.selectNodeContents(pre.querySelector("code") ?? pre);
      const selection = window.getSelection();
      selection?.removeAllRanges();
      selection?.addRange(range);
    };

    button.addEventListener("click", async () => {
      const code = (pre.querySelector("code")?.innerText ?? pre.innerText).replace(/^Copy\n/, "");
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(code);
          button.textContent = "Copied";
        } else {
          selectCode();
          button.textContent = "Selected";
        }
      } catch (_error) {
        selectCode();
        button.textContent = "Selected";
      }
      window.setTimeout(() => { button.textContent = "Copy"; }, 1400);
    });
    pre.appendChild(button);
  });

  const tocLinks = Array.from(document.querySelectorAll(".page-toc a"));
  const byId = new Map(tocLinks.map((link) => [decodeURIComponent(link.hash.slice(1)), link]));
  const headings = Array.from(document.querySelectorAll(".api-content h2[id], .api-content h3[id]"));

  if ("IntersectionObserver" in window && headings.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting).at(-1);
        if (!visible) return;
        tocLinks.forEach((link) => link.classList.remove("current"));
        byId.get(visible.target.id)?.classList.add("current");
      },
      { rootMargin: "-15% 0px -75% 0px" }
    );
    headings.forEach((heading) => observer.observe(heading));
  }
})();
