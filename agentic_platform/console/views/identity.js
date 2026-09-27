import { api, badge, h, short } from "../app.js";

export default {
  id: "identity",
  title: "Identity",
  refreshMs: 3000,
  async render() {
    const data = await api("/identity");
    const you = data.principal;
    const grants = data.grants.map((g) => h("tr", {},
      h("td", { class: "mono" }, h("a", { href: `#runs/${g.run_id}` }, short(g.run_id))),
      h("td", {}, [...g.actors, g.subject].join(" → ")),
      h("td", { class: "mono" }, g.audience), h("td", { class: "mono" }, g.scope),
      h("td", {}, new Date(g.expires * 1000).toLocaleTimeString()), h("td", {}, g.live ? badge("active") : badge("revoked"))));
    const refs = data.credential_refs.map((c) => h("tr", {}, h("td", { class: "mono" }, c.ref), h("td", {}, c.consumers.join(", ")),
      h("td", { class: "muted" }, "value never leaves the store")));
    const access = data.secret_access.map((a) => h("tr", {}, h("td", {}, new Date(a.ts * 1000).toLocaleTimeString()),
      h("td", { class: "mono" }, a.ref), h("td", {}, a.consumer), h("td", {}, badge(a.decision === "released" ? "allow" : "deny"))));
    return h("section", {},
      h("h1", {}, "Identity and credentials"),
      h("p", { class: "lede" }, "Each run acts on behalf of a user. The platform mints a short-lived, audience-bound token for the "
        + "agent, and every child or remote agent receives a narrower token that extends the actor chain. Tokens are never stored with a run."),
      h("div", { class: "stats" },
        h("div", { class: "stat" }, h("b", {}, you.sub), h("span", {}, "signed-in subject")),
        h("div", { class: "stat" }, h("b", {}, `${you.tenant} · ${you.role}`), h("span", {}, "tenant and role")),
        h("div", { class: "stat" }, h("b", {}, you.expires ? new Date(you.expires * 1000).toLocaleTimeString() : you.auth),
          h("span", {}, "token expires"))),
      h("h2", {}, "Delegation grants (your tenant)"),
      grants.length ? h("table", {}, h("tr", {}, ["Run", "Actor chain (acting → on behalf of)", "Audience", "Scope", "Expires", "Token"]
        .map((t) => h("th", {}, t))), grants) : h("p", { class: "muted" }, "No run has been delegated yet."),
      h("h2", {}, "Credential store"),
      h("table", {}, h("tr", {}, ["Reference", "Released only to", ""].map((t) => h("th", {}, t))), refs),
      you.role === "operator" ? h("div", {}, h("h2", {}, "Secret releases"),
        h("table", {}, h("tr", {}, ["Time", "Reference", "Consumer", "Decision"].map((t) => h("th", {}, t))), access))
        : h("p", { class: "muted" }, "Operators can see the secret release audit."));
  },
};
