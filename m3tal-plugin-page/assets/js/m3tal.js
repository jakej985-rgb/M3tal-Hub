document.addEventListener('DOMContentLoaded', () => {
  const header = document.getElementById('m3tal-global-header');
  if (header && !header.hasChildNodes()) {
    header.innerHTML = `
      <nav class="m3tal-nav">
        <a class="m3tal-nav-brand" href="../">
          <span>⚙️</span>
          <span>M3TAL HUB</span>
        </a>
        <div class="m3tal-nav-links">
          <a class="m3tal-nav-link" href="../">Hub Home</a>
          <a class="m3tal-nav-link" href="https://github.com/jakej985-rgb/m3tal-plugin-page" target="_blank" rel="noopener noreferrer">Plugin Repo</a>
          <a class="m3tal-nav-link" href="https://github.com/jakej985-rgb/m3tal-core" target="_blank" rel="noopener noreferrer">M3tal Core</a>
        </div>
      </nav>
    `;
  }

  const footer = document.getElementById('m3tal-global-footer');
  if (footer && !footer.hasChildNodes()) {
    footer.innerHTML = `
      <div class="m3tal-container" style="padding: 0;">
        <p>M3TAL Plugins Directory &bull; Part of the M3tal Application Ecosystem</p>
      </div>
    `;
  }
});
