// Pure RCKG Thin Human Governance Portal Client Logic

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadDashboardData();
  loadGapsData();
  loadMatrixData();
  loadAuditLogs();
  initPlayground();
  initModal();
});

// Toast Helper
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// 1. Tab Navigation
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetTab = tab.dataset.tab;
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      document.getElementById(`panel-${targetTab}`).classList.add("active");
    });
  });
}

// 2. Executive Dashboard & Heatmap
async function loadDashboardData() {
  try {
    const res = await fetch("/api/v1/coverage/summary");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("stat-obls").textContent = data.total_obligations;
    document.getElementById("stat-ctrls").textContent = data.active_controls;
    document.getElementById("stat-mappings").textContent = data.total_linkages;
    document.getElementById("stat-full-cov").textContent = `${data.coverage_rates.full_coverage_pct}%`;

    // Render Chapter Heatmap
    const heatmapContainer = document.getElementById("chapter-heatmap");
    heatmapContainer.innerHTML = "";
    data.chapter_breakdown.forEach(ch => {
      const card = document.createElement("div");
      card.className = "chapter-card";
      card.innerHTML = `
        <div class="chapter-header">
          <span class="chapter-title">${ch.chapter}</span>
          <span class="chapter-pct">${ch.coverage_pct}%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${ch.coverage_pct}%"></div>
        </div>
        <div class="chapter-stats">
          <span>Total: ${ch.total_obligations}</span>
          <span>Full: ${ch.fully_covered}</span>
          <span>Partial: ${ch.partially_covered}</span>
          <span>Uncovered: ${ch.uncovered}</span>
        </div>
      `;
      heatmapContainer.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

// 3. Load Gaps Data
async function loadGapsData() {
  try {
    const res = await fetch("/api/v1/gaps?framework=MAS-TRM");
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("stat-gaps").textContent = data.total_true_gaps;
    const tbody = document.getElementById("gaps-table-body");
    tbody.innerHTML = "";

    const allGaps = [...data.category_b_retail_mandates, ...data.category_a_unmatched];
    if (allGaps.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No compliance gaps identified.</td></tr>`;
      return;
    }

    allGaps.forEach(g => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong style="color: var(--accent-indigo);">${g.obligation_id}</strong></td>
        <td>${g.statement_text}</td>
        <td><span class="badge badge-none">${g.category}</span></td>
        <td style="color: var(--text-secondary);">${g.audit_root_cause}</td>
        <td style="color: #34d399;">${g.suggested_remediation}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load gaps:", err);
  }
}

// 4. Load Crosswalk Matrix
async function loadMatrixData() {
  const searchVal = document.getElementById("matrix-search")?.value || "";
  const relVal = document.getElementById("filter-relation")?.value || "";
  const covVal = document.getElementById("filter-coverage")?.value || "";

  let url = `/api/v1/crosswalk?limit=100`;
  if (relVal) url += `&semantic_relation=${relVal}`;
  if (covVal) url += `&assurance_coverage=${covVal}`;

  try {
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById("matrix-table-body");
    tbody.innerHTML = "";

    let items = data.items;
    if (searchVal) {
      const s = searchVal.toLowerCase();
      items = items.filter(i => 
        i.source_id.toLowerCase().includes(s) || 
        i.target_id.toLowerCase().includes(s) ||
        i.source_text.toLowerCase().includes(s) ||
        i.target_name.toLowerCase().includes(s)
      );
    }

    items.forEach(item => {
      const covBadgeClass = item.assurance_coverage === "FULL_COVERAGE" ? "badge-full" : 
                            (item.assurance_coverage === "PARTIAL_COVERAGE" ? "badge-partial" : "badge-none");
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${item.source_id}</strong><div style="font-size: 0.78rem; color: var(--text-muted);">${item.source_text.slice(0, 80)}...</div></td>
        <td><strong>${item.target_id}</strong><div style="font-size: 0.78rem; color: var(--text-muted);">${item.target_name}</div></td>
        <td><span class="badge badge-relation">${item.semantic_relation}</span></td>
        <td><span class="badge ${covBadgeClass}">${item.assurance_coverage}</span></td>
        <td><strong>${(item.confidence_score * 100).toFixed(0)}%</strong></td>
        <td><div style="font-size: 0.78rem; color: var(--text-secondary); max-width: 320px;">${item.rationale || "N/A"}</div></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="openOverrideModal('${item.mapping_id}', '${item.source_id}', '${item.target_id}', '${item.semantic_relation}', '${item.assurance_coverage}')">
            Override
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load matrix data:", err);
  }
}

document.getElementById("matrix-search")?.addEventListener("input", loadMatrixData);
document.getElementById("filter-relation")?.addEventListener("change", loadMatrixData);
document.getElementById("filter-coverage")?.addEventListener("change", loadMatrixData);
document.getElementById("btn-reload-matrix")?.addEventListener("click", loadMatrixData);

// 5. Auditor Override Modal
function initModal() {
  document.getElementById("btn-cancel-override").addEventListener("click", () => {
    document.getElementById("override-modal").classList.remove("active");
  });

  document.getElementById("btn-save-override").addEventListener("click", async () => {
    const mappingId = document.getElementById("override-mapping-id").value;
    const semRel = document.getElementById("override-rel-select").value;
    const assCov = document.getElementById("override-cov-select").value;
    const auditorId = document.getElementById("override-auditor-id").value;
    const justification = document.getElementById("override-justification").value;

    if (!justification || justification.length < 5) {
      showToast("Please provide a defensible audit justification.", "warning");
      return;
    }

    try {
      const res = await fetch(`/api/v1/mappings/${mappingId}/override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          semantic_relation: semRel,
          assurance_coverage: assCov,
          auditor_id: auditorId,
          justification: justification
        })
      });

      if (res.ok) {
        showToast("Auditor override applied & immutable audit log created!");
        document.getElementById("override-modal").classList.remove("active");
        loadMatrixData();
        loadAuditLogs();
        loadDashboardData();
      } else {
        showToast("Failed to apply override.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("Error submitting override.", "error");
    }
  });
}

window.openOverrideModal = function(id, srcId, tgtId, currentRel, currentCov) {
  document.getElementById("override-mapping-id").value = id;
  document.getElementById("override-context-label").textContent = `${srcId} ⟷ ${tgtId}`;
  document.getElementById("override-rel-select").value = currentRel;
  document.getElementById("override-cov-select").value = currentCov;
  document.getElementById("override-justification").value = "";
  document.getElementById("override-modal").classList.add("active");
};

// 6. Realtime NLI Playground
function initPlayground() {
  document.getElementById("btn-run-eval")?.addEventListener("click", async () => {
    const src = document.getElementById("play-source").value;
    const tgt = document.getElementById("play-target").value;

    if (!src || !tgt) {
      showToast("Please provide both source and target texts.", "warning");
      return;
    }

    const btn = document.getElementById("btn-run-eval");
    btn.textContent = "⏳ Evaluating...";
    btn.disabled = true;

    try {
      const res = await fetch("/api/v1/evaluation/realtime", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_text: src, target_text: tgt })
      });

      if (res.ok) {
        const data = await res.json();
        document.getElementById("eval-result-card").style.display = "block";
        document.getElementById("res-relation").textContent = data.semantic_relation;
        
        const covEl = document.getElementById("res-coverage");
        covEl.textContent = data.assurance_coverage;
        covEl.className = "badge " + (data.assurance_coverage === "FULL_COVERAGE" ? "badge-full" : 
                                      (data.assurance_coverage === "PARTIAL_COVERAGE" ? "badge-partial" : "badge-none"));
        
        document.getElementById("res-confidence").textContent = `${(data.confidence_score * 100).toFixed(0)}%`;
        document.getElementById("res-rationale").textContent = data.rationale;
        showToast("Dual-Judge evaluation completed!");
      }
    } catch (err) {
      console.error(err);
      showToast("Evaluation error.", "error");
    } finally {
      btn.textContent = "⚡ Run Dual-Judge Evaluation";
      btn.disabled = false;
    }
  });
}

// 7. Load Immutable Audit Logs
async function loadAuditLogs() {
  try {
    const res = await fetch("/api/v1/audit-logs?limit=50");
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById("audit-table-body");
    tbody.innerHTML = "";

    if (data.items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No audit logs recorded yet.</td></tr>`;
      return;
    }

    data.items.forEach(log => {
      const timeStr = log.timestamp ? new Date(log.timestamp).toLocaleString() : "N/A";
      const summary = log.event_data?.justification || JSON.stringify(log.event_data);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">${timeStr}</td>
        <td><span class="badge badge-relation">${log.event_type}</span></td>
        <td><strong>${log.actor_id || "system"}</strong></td>
        <td><span class="badge badge-partial">${log.actor_type || "service"}</span></td>
        <td style="font-size: 0.82rem; color: var(--text-secondary);">${summary}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load audit logs:", err);
  }
}
