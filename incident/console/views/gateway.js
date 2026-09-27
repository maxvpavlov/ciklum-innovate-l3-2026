import { api, badge, h, short } from "../app.js";

export default {
  id: "gateway",
  title: "Gateway",
  refreshMs: 3000,
  async render() {
    const data = await api("/gateway");
    const servers = data.servers.map((s) => h("article", { class: "card" },
      h("div", { class: "num" }, `${s.transport} · tenants ${s.tenants.join(", ")} · sessions launched ${s.sessions_launched}`),
      h("h3", {}, s.name, " ", badge(s.status === "pinned" ? "active" : s.status === "quarantined" ? "denied" : s.status)),
      h("table", {}, h("tr", {}, ["Tool", "Risk", "Pinned definition"].map((t) => h("th", {}, t))),
        s.tools.map((t) => h("tr", {}, h("td", { class: "mono" }, t.name), h("td", {}, t.risk),
          h("td", { class: "mono", title: t.pinned_sha256 ?? "" }, t.pinned_sha256 ? short(t.pinned_sha256) : s.transport === "local" ? "in-process handler" : "not yet connected"))))));
    const policy = Object.entries(data.policy).map(([key, value]) =>
      h("div", { class: "stat" }, h("b", {}, Array.isArray(value) ? value.join(", ") : value), h("span", {}, key.replaceAll("_", " "))));
    const audit = data.audit.map((a) => h("tr", {},
      h("td", {}, new Date(a.ts * 1000).toLocaleTimeString()),
      h("td", { class: "mono" }, h("a", { href: `#runs/${a.run_id}` }, short(a.run_id))),
      h("td", {}, a.role), h("td", { class: "mono" }, a.tool), h("td", {}, a.server ?? ""),
      h("td", {}, badge(a.decision)), h("td", { class: "mono" }, a.reason), h("td", { class: "mono", title: a.args_sha256 }, short(a.args_sha256))));
    return h("section", {},
      h("h1", {}, "Tool gateway"),
      h("p", { class: "lede" }, "Every agent tool call passes one policy and audit point. Upstream MCP sessions are shared "
        + "per server and tenant, and each tool definition is pinned when the gateway first connects."),
      h("h2", {}, "Policy"), h("div", { class: "stats" }, policy),
      h("h2", {}, "Tool servers"), h("div", { class: "grid wide" }, servers),
      h("h2", {}, "Audit (your tenant)"),
      audit.length ? h("table", {}, h("tr", {}, ["Time", "Run", "Role", "Tool", "Server", "Decision", "Reason or outcome", "Args hash"]
        .map((t) => h("th", {}, t))), audit) : h("p", { class: "muted" }, "No tool calls yet."));
  },
};
