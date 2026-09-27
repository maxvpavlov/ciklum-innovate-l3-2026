import { api, badge, h, short } from "../app.js";

export default {
  id: "approvals",
  title: "Approvals",
  refreshMs: 3000,
  async render({ who, navigate }) {
    const header = [h("h1", {}, "Approvals"),
      h("p", { class: "lede" }, "An approval binds to the exact proposed action and arguments. "
        + "Approving and resuming are separate decisions.")];
    if (who.role !== "operator") {
      return h("section", {}, header, h("div", { class: "notice" }, "Only an operator identity can decide approvals."));
    }
    const waiting = (await api("/runs")).filter((r) => r.status === "waiting_approval");
    const cards = await Promise.all(waiting.map(async (summary) => {
      const run = await api(`/runs/${encodeURIComponent(summary.id)}`);
      if (!run.proposal) return "";
      const decide = (decision) => async () => {
        await api(`/runs/${encodeURIComponent(run.id)}/decision`, { method: "POST", body: { key: run.proposal.key, decision } });
        navigate("approvals");
      };
      const resume = async () => { await api(`/runs/${encodeURIComponent(run.id)}/resume`, { method: "POST" }); navigate(`runs/${run.id}`); };
      return h("article", { class: "card" },
        h("div", { class: "num" }, "Run ", h("a", { href: `#runs/${run.id}` }, short(run.id)), " ", badge(run.status)),
        h("h3", {}, run.proposal.name),
        h("pre", {}, JSON.stringify(run.proposal.args, null, 2)),
        h("p", { class: "mono muted" }, `action key ${short(run.proposal.key, 16)}`),
        run.approved
          ? h("p", { class: "actions" }, badge("approved"), h("button", { onclick: resume }, "Resume run"))
          : h("p", { class: "actions" }, h("button", { onclick: decide("approve") }, "Approve"),
              h("button", { class: "danger", onclick: decide("deny") }, "Deny")));
    }));
    return h("section", {}, header,
      waiting.length ? h("div", { class: "grid" }, cards) : h("p", { class: "muted" }, "No action is waiting for approval."));
  },
};
