import { api, badge, h } from "../app.js";

export default {
  id: "overview",
  title: "Overview",
  async render() {
    const map = await api("/platform");
    const stats = Object.entries(map.counts).map(([key, value]) =>
      h("div", { class: "stat" }, h("b", {}, value), h("span", {}, key.replaceAll("_", " "))));
    const cards = map.components.map((c) =>
      h("article", { class: `card ${c.status}` },
        h("div", { class: "num" }, `Session ${String(c.lesson).padStart(2, "0")} `, badge(c.status)),
        h("h3", {}, c.name), h("p", {}, c.summary)));
    return h("section", {},
      h("h1", {}, "Platform map"),
      h("p", { class: "lede" }, `Checkpoint lesson-${String(map.checkpoint).padStart(2, "0")}. `
        + "Built components are live in this platform; planned components arrive in later sessions."),
      h("div", { class: "stats" }, stats), h("div", { class: "grid" }, cards));
  },
};
