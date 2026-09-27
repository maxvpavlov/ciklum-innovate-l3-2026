import { api, badge, h, route, short } from "../app.js";

export default {
  id: "registry",
  title: "Registry",
  async render({ who }) {
    const data = await api("/registry");
    const activate = (agent) => async () => {
      await api(`/registry/agents/${encodeURIComponent(agent.name)}/activate`, { method: "POST", body: { version: agent.version } });
      route();
    };
    const rows = data.agents.map((a) => h("tr", {},
      h("td", {}, h("b", {}, a.name), h("div", { class: "muted" }, a.spec.description)),
      h("td", {}, `v${a.version}`), h("td", {}, a.active ? badge("active") : badge(a.state)),
      h("td", {}, a.spec.kind), h("td", {}, a.spec.owner),
      h("td", { class: "mono" }, a.spec.allowed.join(", ")), h("td", {}, a.spec.skills.join(", ")),
      h("td", { class: "mono", title: a.sha256 }, short(a.sha256)),
      h("td", {}, who.role === "operator" && !a.active && a.state !== "retired"
        ? h("button", { class: "secondary", onclick: activate(a) }, "Activate") : "")));
    const remotes = data.remote_agents.map((r) => h("tr", {},
      h("td", {}, h("b", {}, r.name)), h("td", { class: "mono" }, r.url), h("td", {}, r.skills.join(", ")),
      h("td", { class: "mono", title: r.sha256 }, short(r.sha256))));
    return h("section", {},
      h("h1", {}, "Agent registry"),
      h("p", { class: "lede" }, "Immutable, versioned agent definitions and pinned remote agents. "
        + "A run records the exact version and content hash it used."),
      h("table", {}, h("tr", {}, ["Agent", "Version", "State", "Kind", "Owner", "Tools", "Skills", "SHA-256", ""]
        .map((t) => h("th", {}, t))), rows),
      h("h2", {}, "Remote agents (A2A)"),
      remotes.length ? h("table", {}, h("tr", {}, ["Name", "Endpoint", "Skills", "Pinned card"].map((t) => h("th", {}, t))), remotes)
        : h("p", { class: "muted" }, "No remote agent is registered. Start the A2A specialist and set A2A_URL."));
  },
};
