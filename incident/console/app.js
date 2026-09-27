// Platform console shell. Every value from the API is rendered as text, never as HTML:
// model answers, tool evidence and run events are untrusted data.
import views from "./views/index.js";

const TOKEN = "platform-console-token";
let who = null;

export function h(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key === "class") node.className = value;
    else node.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of children.flat()) {
    if (child === undefined || child === null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

export function badge(status) {
  const tone = { completed: "ok", built: "ok", allow: "ok", active: "info", queued: "info", running: "info",
    waiting_approval: "warn", approval_required: "warn", planned: "", failed: "bad", denied: "bad",
    rejected: "bad", deny: "bad", cancelled: "", retired: "" }[status] ?? "";
  return h("span", { class: `badge ${tone}` }, status ?? "unknown");
}

export const short = (value, size = 12) => (value ? String(value).slice(0, size) : "");

export async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${sessionStorage.getItem(TOKEN) ?? ""}`,
               ...(options.headers ?? {}) },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) { signOut(); throw new Error("Signed out: the credential was rejected."); }
  if (!response.ok) throw new Error(`${response.status} ${data.detail ?? response.statusText}`);
  return data;
}

async function signIn(credential) {
  sessionStorage.setItem(TOKEN, credential);
  who = await api("/whoami");
}

function signOut() {
  sessionStorage.removeItem(TOKEN);
  who = null;
  route();
}

function loginView() {
  const input = h("input", { name: "credential", required: true, autocomplete: "off", placeholder: "demo-acme" });
  const status = h("div");
  const form = h("form", { onsubmit: async (event) => {
    event.preventDefault();
    try { await signIn(input.value.trim()); route(); }
    catch (error) { status.replaceChildren(h("div", { class: "error" }, error.message)); }
  } },
    h("label", {}, "Demo credential", input),
    h("p", { class: "muted" }, "Local demo identities: demo-acme (analyst), demo-operator (operator), demo-globex (analyst). "
      + "They are for loopback use only."),
    h("button", { type: "submit" }, "Sign in"));
  return h("section", { class: "panel login" }, h("h1", {}, "Sign in"), status, form);
}

let timer = null;

export async function route() {
  clearInterval(timer);
  const main = document.getElementById("view");
  const nav = document.getElementById("nav");
  if (!who && sessionStorage.getItem(TOKEN)) {
    try { who = await api("/whoami"); } catch { who = null; }
  }
  if (!who) {
    nav.replaceChildren();
    document.getElementById("who").replaceChildren();
    main.replaceChildren(loginView());
    return;
  }
  const [name, ...rest] = (location.hash.slice(1) || "overview").split("/");
  const view = views.find((v) => v.id === name) ?? views[0];
  nav.replaceChildren(...views.map((v) => h("a", { href: `#${v.id}`, "aria-current": v === view ? "page" : false }, v.title)));
  document.getElementById("who").replaceChildren(
    h("span", {}, `${who.tenant} · ${who.role}`), h("button", { class: "secondary", onclick: signOut }, "Sign out"));
  const context = { who, param: rest.join("/"), navigate: (hash) => { location.hash = hash; } };
  const render = async () => {
    try { main.replaceChildren(await view.render(context)); }
    catch (error) { main.replaceChildren(h("div", { class: "error" }, error.message)); }
  };
  await render();
  if (view.refreshMs) timer = setInterval(render, view.refreshMs);
}

window.addEventListener("hashchange", route);
route();
