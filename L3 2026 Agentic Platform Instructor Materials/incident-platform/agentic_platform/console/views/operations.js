import { api, badge, h } from "../app.js";

const number = (value, digits = 1) => (typeof value === "number" ? value.toFixed(digits) : value);

export default {
  id: "operations",
  title: "Operations",
  refreshMs: 2000,
  async render() {
    const data = await api("/operations");
    const stats = [
      [`${data.admission.pending} / ${data.admission.max_pending}`, "admitted runs / queue limit"],
      [data.admission.per_second_per_tenant, "submissions per second per tenant"],
      [`${data.active_runs} / ${data.workers}`, "active runs / workers"],
      [data.shared_team_budget, "shared team token budget"],
    ].map(([value, label]) => h("div", { class: "stat" }, h("b", {}, value), h("span", {}, label)));
    const statuses = Object.entries(data.run_status_counts).map(([status, count]) =>
      h("div", { class: "stat" }, h("b", {}, count), h("span", {}, badge(status))));
    const releases = data.releases.map((r) => h("tr", {},
      h("td", {}, new Date(r.ts * 1000).toLocaleString()), h("td", {}, h("b", {}, r.agent), ` v${r.baseline_version} → v${r.candidate_version}`),
      h("td", {}, `${number(r.baseline.success_rate * 100, 0)}% → ${number(r.candidate.success_rate * 100, 0)}%`),
      h("td", {}, `${number(r.baseline.mean_tokens)} → ${number(r.candidate.mean_tokens)}`),
      h("td", {}, `${number(r.baseline.mean_latency_ms)} → ${number(r.candidate.mean_latency_ms)} ms`),
      h("td", {}, Object.entries(r.checks).map(([check, ok]) => h("div", {}, badge(ok ? "allow" : "deny"), " ", check))),
      h("td", {}, r.approved ? badge("completed") : badge("rejected"), " ", r.activated ? "activated" : "not activated")));
    return h("section", {},
      h("h1", {}, "Operations"),
      h("p", { class: "lede" }, "Admission control, worker capacity and evaluated release decisions. "
        + "Usage figures come from the offline fixture and are teaching metrics, not live model cost."),
      h("h2", {}, "Capacity"), h("div", { class: "stats" }, stats),
      h("h2", {}, "Runs by status (your tenant)"), statuses.length ? h("div", { class: "stats" }, statuses) : h("p", { class: "muted" }, "No runs yet."),
      h("h2", {}, "Release decisions"),
      releases.length ? h("table", {}, h("tr", {}, ["Time", "Agent", "Success", "Mean usage", "Mean latency", "Gate checks", "Decision"]
        .map((t) => h("th", {}, t))), releases) : h("p", { class: "muted" }, "No release has been evaluated yet."));
  },
};
