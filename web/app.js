const app = document.getElementById("app");
const session = document.getElementById("session");

const state = {
  token: localStorage.getItem("token"),
  user: JSON.parse(localStorage.getItem("user") || "null"),
  simulation: null,
  performed: [],
  startedAt: 0,
};

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key === "class") node.className = value;
    else node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    node.append(child instanceof Node ? child : document.createTextNode(child));
  }
  return node;
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`/api${path}`, { ...options, headers });
  if (response.status === 401 && state.token) {
    logout();
    throw new Error("Session expired");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function saveSession(data) {
  state.token = data.access_token;
  state.user = data.user;
  localStorage.setItem("token", state.token);
  localStorage.setItem("user", JSON.stringify(state.user));
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  render();
}

function renderSession() {
  session.replaceChildren();
  if (!state.user) return;
  session.append(
    `${state.user.name} (${state.user.role}) `,
    el("button", { class: "link", onclick: logout }, "Sign out")
  );
}

function showError(container, message) {
  container.querySelector(".error")?.remove();
  container.prepend(el("div", { class: "error" }, message));
}

function renderAuth() {
  let mode = "login";
  const box = el("div", { class: "card" });

  function draw() {
    box.replaceChildren(
      el("h2", {}, mode === "login" ? "Sign in" : "Create account"),
      mode === "register" ? el("input", { id: "name", placeholder: "Full name" }) : "",
      el("input", { id: "email", type: "email", placeholder: "Email" }),
      el("input", { id: "password", type: "password", placeholder: "Password (8 characters minimum)" }),
      mode === "register"
        ? el(
            "select",
            { id: "role" },
            ["independent", "student", "educator", "institution_admin"].map((r) => el("option", { value: r }, r))
          )
        : "",
      el("div", { class: "row" },
        el("button", { class: "primary", onclick: submit }, mode === "login" ? "Sign in" : "Register"),
        el("button", { onclick: () => { mode = mode === "login" ? "register" : "login"; draw(); } },
          mode === "login" ? "Create an account" : "Have an account")
      )
    );
  }

  async function submit() {
    const body = {
      email: box.querySelector("#email").value,
      password: box.querySelector("#password").value,
    };
    if (mode === "register") {
      body.name = box.querySelector("#name").value;
      body.role = box.querySelector("#role").value;
    }
    try {
      saveSession(await api(`/auth/${mode}`, { method: "POST", body: JSON.stringify(body) }));
      render();
    } catch (error) {
      showError(box, error.message);
    }
  }

  draw();
  app.replaceChildren(box);
}

async function renderHome() {
  const [simulations, attempts] = await Promise.all([api("/simulations"), api("/attempts")]);
  app.replaceChildren(
    el("h2", {}, "Simulations"),
    ...simulations.map((s) =>
      el("div", { class: "card" },
        el("strong", {}, s.title),
        el("div", {}, `${s.area} - ${s.step_count} steps`),
        el("p", {}, s.description),
        el("button", { class: "primary", onclick: () => startSimulation(s.id) }, "Start")
      )
    ),
    el("h2", {}, "Recent attempts"),
    attempts.length
      ? el("table", {},
          el("tr", {}, ["Simulation", "Score", "Time", "Date"].map((h) => el("th", {}, h))),
          attempts.map((a) =>
            el("tr", {},
              el("td", {}, a.simulation_id),
              el("td", {}, `${a.score}/${a.max_score}`),
              el("td", {}, `${a.duration_seconds}s`),
              el("td", {}, new Date(a.created_at).toLocaleString())
            )
          )
        )
      : el("p", {}, "No attempts yet.")
  );
}

async function startSimulation(id) {
  state.simulation = await api(`/simulations/${id}`);
  state.performed = [];
  state.startedAt = Date.now();
  renderSimulation();
}

function renderSimulation() {
  const sim = state.simulation;
  const performedList = el("ol", {}, state.performed.map((id) => el("li", {}, sim.actions.find((a) => a.id === id).label)));

  app.replaceChildren(
    el("button", { class: "link", onclick: render }, "Back"),
    el("h2", {}, sim.title),
    el("p", {}, sim.description),
    el("h3", {}, "Procedure"),
    el("ol", { class: "steps" },
      sim.steps.map((s) => el("li", {}, s.instruction, " ", el("span", { class: "hint" }, s.hint)))
    ),
    el("h3", {}, "Your actions"),
    performedList,
    el("div", { class: "row actions" },
      sim.actions.map((a) =>
        el("button", { onclick: () => { state.performed.push(a.id); renderSimulation(); } }, a.label)
      )
    ),
    el("div", { class: "row", style: "margin-top: 16px" },
      el("button", { class: "primary", onclick: submitAttempt }, "Submit"),
      el("button", { onclick: () => { state.performed = []; renderSimulation(); } }, "Reset")
    )
  );
}

async function submitAttempt() {
  const duration = Math.round((Date.now() - state.startedAt) / 1000);
  try {
    const result = await api("/attempts", {
      method: "POST",
      body: JSON.stringify({
        simulation_id: state.simulation.id,
        actions: state.performed,
        duration_seconds: duration,
      }),
    });
    renderResult(result);
  } catch (error) {
    showError(app, error.message);
  }
}

function describeError(error) {
  const label = state.simulation.actions.find((a) => a.id === error.action)?.label || error.action;
  const kinds = {
    out_of_order: "Done out of order",
    repeated: "Repeated",
    wrong_action: "Incorrect action",
    missing: "Not done",
  };
  return `${kinds[error.type] || error.type}: ${label}`;
}

function renderResult(result) {
  app.replaceChildren(
    el("h2", {}, "Result"),
    el("div", { class: "card" }, el("strong", {}, `${result.score} / ${result.max_score}`), ` in ${result.duration_seconds}s`),
    result.errors.length
      ? el("ul", {}, result.errors.map((e) => el("li", {}, describeError(e))))
      : el("p", {}, "No errors."),
    el("div", { class: "row" },
      el("button", { class: "primary", onclick: () => startSimulation(state.simulation.id) }, "Try again"),
      el("button", { onclick: render }, "Home")
    )
  );
}

async function render() {
  renderSession();
  if (!state.token) return renderAuth();
  try {
    await renderHome();
  } catch (error) {
    showError(app, error.message);
  }
}

render();
