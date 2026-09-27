import { api, badge, h, short } from "../app.js";

const TERMINAL = new Set(["completed", "failed", "denied", "cancelled", "rejected"]);

function eventLine(event) {
  const detail = Object.entries(event)
    .filter(([key]) => !["kind", "run_id", "parent_id"].includes(key))
    .map(([key, value]) => `${key}=${typeof value === "object" ? JSON.stringify(value) : value}`).join("  ");
  return h("li", { class: event.kind === "failure" || event.ok === false ? "fail" : "" },
    h("b", {}, event.kind), " ", h("span", { class: "mono muted" }, detail));
}

async function detail(id, navigate) {
  const run = await api(`/runs/${encodeURIComponent(id)}`);
  const config = run.configuration ?? {};
  const cancel = async () => { await api(`/runs/${encodeURIComponent(id)}/cancel`, { method: "POST" }); navigate(`runs/${id}`); };
  return h("section", {},
    h("p", {}, h("a", { href: "#runs" }, "All runs")),
    h("h1", {}, "Run ", h("span", { class: "mono" }, short(run.id, 16)), " ", badge(run.status)),
    h("p", { class: "lede" }, `${config.name ?? "child run"}${config.version ? ` v${config.version}` : ""} · role ${run.role}`
      + ` · ${run.tokens} fixture tokens`, run.parent_id ? h("span", {}, " · parent ",
        h("a", { href: `#runs/${run.parent_id}` }, short(run.parent_id))) : ""),
    TERMINAL.has(run.status) ? "" : h("p", {}, h("button", { class: "danger", onclick: cancel }, "Cancel run")),
    run.error ? h("div", { class: "error" }, `Failure code: ${run.error}`) : "",
    run.proposal ? h("div", { class: "notice" }, `Waiting for an operator decision on ${run.proposal.name}. `,
      h("a", { href: "#approvals" }, "Open approvals")) : "",
    h("div", { class: "row" },
      h("div", {}, h("h2", {}, "Answer"), h("pre", {}, JSON.stringify(run.answer, null, 2))),
      h("div", {}, h("h2", {}, "Events"), h("ol", { class: "timeline" }, run.events.map(eventLine)))),
    run.children.length ? h("div", {}, h("h2", {}, "Child runs"), table(run.children)) : "",
    config.sha256 ? h("p", { class: "muted mono" }, `definition ${config.name}@${config.version} sha256 ${config.sha256}`) : "");
}

function table(runs) {
  return h("table", {}, h("tr", {}, ["Run", "Agent", "Role", "Status", "Tokens", "Error"].map((t) => h("th", {}, t))),
    runs.map((r) => h("tr", { class: "link", onclick: () => { location.hash = `runs/${r.id}`; } },
      h("td", { class: "mono" }, short(r.id)), h("td", {}, r.agent ? `${r.agent} v${r.version}` : "child"),
      h("td", {}, r.role), h("td", {}, badge(r.status)), h("td", {}, r.tokens), h("td", { class: "mono" }, r.error ?? ""))));
}

export default {
  id: "runs",
  title: "Runs",
  refreshMs: 2000,
  async render({ param, navigate }) {
    if (param) return detail(param, navigate);
    const [runs, registry] = await Promise.all([api("/runs"), api("/registry")]);
    const agent = h("select", { name: "agent" }, [...new Set(registry.agents.map((a) => a.name))]
      .map((name) => h("option", { value: name }, name)));
    const incident = h("select", { name: "incident" }, ["INC-001", "INC-002", "INC-003"].map((id) => h("option", { value: id }, id)));
    const status = h("div");
    const form = h("form", { class: "inline", onsubmit: async (event) => {
      event.preventDefault();
      try {
        const run = await api("/runs", { method: "POST", body: { incident_id: incident.value, agent: agent.value } });
        navigate(`runs/${run.id}`);
      } catch (error) { status.replaceChildren(h("div", { class: "error" }, error.message)); }
    } }, h("label", {}, "Incident", incident), h("label", {}, "Agent (active version)", agent), h("button", { type: "submit" }, "Submit run"));
    const top = runs.filter((r) => !r.parent_id);
    return h("section", {},
      h("h1", {}, "Runs"),
      h("p", { class: "lede" }, "Runs for your tenant only. Select a run to see its answer, event timeline and child runs."),
      status, form, top.length ? table(top) : h("p", { class: "muted" }, "No runs yet."));
  },
};
