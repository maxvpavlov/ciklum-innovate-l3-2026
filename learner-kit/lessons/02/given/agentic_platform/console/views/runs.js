import { api, badge, h, short } from "../app.js";

function eventLine(event) {
  const detail = Object.entries(event)
    .filter(([key]) => !["kind", "run_id", "parent_id"].includes(key))
    .map(([key, value]) => `${key}=${typeof value === "object" ? JSON.stringify(value) : value}`).join("  ");
  return h("li", { class: event.kind === "failure" || event.ok === false ? "fail" : "" },
    h("b", {}, event.kind), " ", h("span", { class: "mono muted" }, detail));
}

async function detail(id) {
  const run = await api(`/runs/${encodeURIComponent(id)}`);
  return h("section", {},
    h("p", {}, h("a", { href: "#runs" }, "All runs")),
    h("h1", {}, "Run ", h("span", { class: "mono" }, short(run.id, 16)), " ", badge(run.status)),
    h("p", { class: "lede" }, `${run.incident} · role ${run.role} · ${run.tokens} fixture tokens`),
    run.error ? h("div", { class: "error" }, `Failure code: ${run.error}`) : "",
    h("div", { class: "row" },
      h("div", {}, h("h2", {}, "Answer"), h("pre", {}, JSON.stringify(run.answer, null, 2))),
      h("div", {}, h("h2", {}, "Events"), h("ol", { class: "timeline" }, run.events.map(eventLine)))));
}

function table(runs) {
  return h("table", {}, h("tr", {}, ["Run", "Incident", "Role", "Status", "Tokens", "Error"].map((t) => h("th", {}, t))),
    runs.map((r) => h("tr", { class: "link", onclick: () => { location.hash = `runs/${r.id}`; } },
      h("td", { class: "mono" }, short(r.id)), h("td", {}, r.incident), h("td", {}, r.role),
      h("td", {}, badge(r.status)), h("td", {}, r.tokens), h("td", { class: "mono" }, r.error ?? ""))));
}

export default {
  id: "runs",
  title: "Runs",
  refreshMs: 2000,
  async render({ param, navigate }) {
    if (param) return detail(param);
    const runs = await api("/runs");
    const incident = h("select", { name: "incident" }, ["INC-001", "INC-002", "INC-003"].map((id) => h("option", { value: id }, id)));
    const status = h("div");
    const form = h("form", { class: "inline", onsubmit: async (event) => {
      event.preventDefault();
      try {
        const run = await api("/runs", { method: "POST", body: { incident_id: incident.value } });
        navigate(`runs/${run.id}`);
      } catch (error) { status.replaceChildren(h("div", { class: "error" }, error.message)); }
    } }, h("label", {}, "Incident", incident), h("button", { type: "submit" }, "Submit run"));
    return h("section", {},
      h("h1", {}, "Runs"),
      h("p", { class: "lede" }, "Runs for your tenant only. Select a run to see its answer and event timeline."),
      status, form, runs.length ? table(runs) : h("p", { class: "muted" }, "No runs yet."));
  },
};
