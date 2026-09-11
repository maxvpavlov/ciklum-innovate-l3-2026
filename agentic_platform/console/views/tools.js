import { api, badge, h } from "../app.js";

// Calls a learner can try. Each one meets a different check in the tool boundary.
const PRESETS = [
  ["Read the INC-001 log", "log_lookup", { incident_id: "INC-001" }],
  ["Read with a tenant argument", "log_lookup", { incident_id: "INC-001", tenant: "locomotive" }],
  ["Read with a wrong argument", "log_lookup", { incident: 1 }],
  ["Propose a rollback", "mock_remediate", { incident_id: "INC-001", action: "rollback" }],
  ["Call an unknown tool", "delete_logs", {}],
];

function catalogue(tools) {
  return h("table", {}, h("tr", {}, ["Tool", "Kind", "Your role may use it", "Contract"].map((t) => h("th", {}, t))),
    tools.map((t) => h("tr", {}, h("td", { class: "mono" }, t.name), h("td", {}, t.kind),
      h("td", {}, badge(t.allowed ? "allow" : "deny")), h("td", { class: "muted" }, t.description))));
}

function decisions(entries) {
  if (!entries.length) return h("p", { class: "muted" }, "No calls checked yet.");
  return h("table", {}, h("tr", {}, ["Time", "Role", "Tool", "Arguments", "Decision", "Code"].map((t) => h("th", {}, t))),
    entries.map((d) => h("tr", {}, h("td", {}, new Date(d.at * 1000).toLocaleTimeString()), h("td", {}, d.role),
      h("td", { class: "mono" }, d.name), h("td", { class: "mono" }, JSON.stringify(d.args)),
      h("td", {}, badge(d.decision)), h("td", { class: "mono" }, d.error ?? (d.key ? `key ${d.key.slice(0, 12)}` : "")))));
}

export default {
  id: "tools",
  title: "Tools",
  async render() {
    const data = await api("/tools");
    const name = h("input", { name: "tool", required: true, value: "log_lookup", autocomplete: "off" });
    const args = h("textarea", { name: "args", rows: 3, class: "mono" }, JSON.stringify({ incident_id: "INC-001" }));
    const result = h("div");
    const log = h("div", {}, decisions(data.decisions));
    const send = async (event) => {
      event.preventDefault();
      let parsed;
      try { parsed = JSON.parse(args.value || "{}"); }
      catch { result.replaceChildren(h("div", { class: "error" }, "Arguments must be a JSON object.")); return; }
      try {
        const outcome = await api("/tools/check", { method: "POST", body: { name: name.value.trim(), args: parsed } });
        result.replaceChildren(h("div", { class: "notice" }, "Decision ", badge(outcome.decision),
          outcome.error ? ` · ${outcome.error}` : "", outcome.key ? " · waiting for an approval of this exact action" : ""),
          outcome.result ? h("pre", {}, JSON.stringify(outcome.result, null, 2)) : "");
        log.replaceChildren(decisions((await api("/tools")).decisions));
      } catch (error) { result.replaceChildren(h("div", { class: "error" }, error.message)); }
    };
    const presets = h("div", { class: "actions" }, PRESETS.map(([label, tool, values]) =>
      h("button", { type: "button", class: "secondary", onclick: () => { name.value = tool; args.value = JSON.stringify(values); } }, label)));
    return h("section", {},
      h("h1", {}, "Tools"),
      h("p", { class: "lede" }, "The tools this platform knows, which ones your role may use, and every call you check. "
        + "A check goes through the same tool boundary agents use; a write is never approved from here."),
      h("h2", {}, "Catalogue"), catalogue(data.tools),
      // A Lesson 01 runtime has no tool boundary yet, so there is nothing to check calls against.
      ...(data.boundary === false
        ? [h("div", { class: "notice" }, "The tool boundary is not built yet: Lesson 02 build steps 1 and 2 add it. "
            + "Until then runs call the Lesson 01 readers directly, and calls cannot be checked here.")]
        : [h("h2", {}, "Try a call"), presets,
          h("form", { class: "inline", onsubmit: send }, h("label", {}, "Tool", name), h("label", {}, "Arguments (JSON)", args),
            h("button", { type: "submit" }, "Check the call")),
          result,
          h("h2", {}, "Decisions"), log]));
  },
};
