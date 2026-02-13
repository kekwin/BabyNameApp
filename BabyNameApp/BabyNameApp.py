from flask import Flask, request, redirect, url_for, render_template_string, session
import os
import json
import random


app = Flask(__name__)
app.secret_key = os.environ.get("BABYNAME_SECRET", "dev-secret-change-me")

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"names": [], "votes": {}}  # votes: { username: { name: {"liked": bool, "comment": str} } }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"names": [], "votes": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


base_layout = """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Baby Name App</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
      body { padding-top: 4.5rem; }
      .actions { display:flex; gap:0.75rem; justify-content:center; flex-wrap:wrap; }
      .col-stack { display:flex; flex-direction:column; gap:0.5rem; align-items:center; }
      .name-title { font-size: 2rem; font-weight: 700; text-align: center; }
      /* Restore colored buttons for vote actions */
      .ok { background:#2ecc71; color:white; border:none; padding:0.5rem 1rem; border-radius:0.5rem; cursor:pointer; }
      .no { background:#e74c3c; color:white; border:none; padding:0.5rem 1rem; border-radius:0.5rem; cursor:pointer; }
      .neutral { background:#3498db; color:white; border:none; padding:0.5rem 1rem; border-radius:0.5rem; cursor:pointer; }
      .undo { background:#f39c12; color:white; border:none; padding:0.5rem 1rem; border-radius:0.5rem; cursor:pointer; }
      .ok:hover { filter: brightness(0.95); }
      .no:hover { filter: brightness(0.95); }
      .neutral:hover { filter: brightness(0.95); }
      .undo:hover { filter: brightness(0.95); }
    </style>
  </head>
  <body>
    <nav class=\"navbar navbar-expand-lg navbar-dark bg-dark fixed-top\">
      <div class=\"container\">
        <a class=\"navbar-brand\" href=\"{{ url_for('index') }}\">Baby Navne</a>
        <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#navbarNav\" aria-controls=\"navbarNav\" aria-expanded=\"false\" aria-label=\"Toggle navigation\">
          <span class=\"navbar-toggler-icon\"></span>
        </button>
        <div class=\"collapse navbar-collapse\" id=\"navbarNav\">
          <ul class=\"navbar-nav ms-auto\">
            <li class=\"nav-item\"><a class=\"nav-link\" href=\"{{ url_for('add_names') }}\">Tilføj navne</a></li>
            <li class=\"nav-item\"><a class=\"nav-link\" href=\"{{ url_for('start') }}\">Start</a></li>
            <li class=\"nav-item\"><a class=\"nav-link\" href=\"{{ url_for('results') }}\">Resultater</a></li>
          </ul>
        </div>
      </div>
    </nav>
    <main class=\"container my-4\">
      {{ content|safe }}
    </main>
    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js\"></script>
  </body>
</html>
"""


@app.route("/")
def index():
    data = load_data()
    content = """
      <div class=\"row\">
        <div class=\"col-lg-8\">
          <div class=\"alert alert-info\" role=\"alert\">
            Velkommen! Tilføj en liste med navne, og gennemgå dem én efter én. I kan synes godt eller dårligt om hvert navn og tilføje en valgfri kommentar.
          </div>
        </div>
        <div class=\"col-lg-4\">
          <div class=\"card\">
            <div class=\"card-body\">
              <h5 class=\"card-title\">Status</h5>
              <p class=\"card-text\">Der er <strong>{{ data.names|length }}</strong> navne i listen.</p>
              <a href=\"{{ url_for('add_names') }}\" class=\"btn btn-primary\">Tilføj navne</a>
              <a href=\"{{ url_for('start') }}\" class=\"btn btn-success ms-2\">Start</a>
            </div>
          </div>
        </div>
      </div>
    """
    inner = render_template_string(content, data=data)
    return render_template_string(base_layout, content=inner)


@app.route("/add", methods=["GET", "POST"])
def add_names():
    data = load_data()
    message = None
    if request.method == "POST":
        text = request.form.get("names", "")
        # Accept comma or newline separated
        incoming = []
        for raw in text.replace("\r", "").split("\n"):
            parts = [p.strip() for p in raw.split(",")]
            for p in parts:
                if p:
                    incoming.append(p)
        # Deduplicate while preserving order
        existing_set = set(n.lower() for n in data["names"])
        for n in incoming:
            if n.lower() not in existing_set:
                data["names"].append(n)
                existing_set.add(n.lower())
        save_data(data)
        message = f"Tilføjede {len(incoming)} navne (duplikater ignoreret)."
    content = """
      <div class=\"card\">
        <div class=\"card-body\">
          <h2 class=\"card-title\">Tilføj navne</h2>
          {% if message %}<div class=\"alert alert-success\" role=\"alert\">{{ message }}</div>{% endif %}
          <form method=\"post\" class=\"mt-2\">
            <div class=\"mb-3\">
              <label for=\"names\" class=\"form-label\">Indsæt navne (kommasepareret eller nye linjer)</label>
              <textarea id=\"names\" name=\"names\" class=\"form-control\" placeholder=\"f.eks. Emma, Olivia, Ava\\n...\">{{ request.form.names or '' }}</textarea>
            </div>
            <button class=\"btn btn-primary\" type=\"submit\">Gem</button>
          </form>
          <p class=\"mt-3\"><strong>Aktuelle navne ({{ data.names|length }}):</strong> {{ data.names|join(', ') }}</p>
        </div>
      </div>
    """
    inner = render_template_string(content, data=data, message=message)
    return render_template_string(base_layout, content=inner)


@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if username:
            session["username"] = username
            session.pop("idx", None)
            return redirect(url_for("swipe"))
    data = load_data()
    users_with_votes = [u for u, v in data.get("votes", {}).items() if v]
    content = """
      <div class=\"card card-center\">
        <div class=\"card-body\">
          <h2 class=\"card-title\">Start</h2>
          <form method=\"post\" class=\"mt-2\">
            <div class=\"mb-3\">
              <label class=\"form-label\">Dit navn</label>
              <input class=\"form-control\" type=\"text\" name=\"username\" placeholder=\"f.eks. Alice\" value=\"\" required>
            </div>
            <div class=\"actions\">
              <button class=\"btn btn-success\" type=\"submit\">Start</button>
            </div>
          </form>
          <p class=\"mt-3\">{{ data.names|length }} navne tilgængelige.</p>
          {% if users_with_votes %}
            <hr>
            <h5>Genoptag en session</h5>
            <ul class=\"list-group\">
              {% for u in users_with_votes %}
                <li class=\"list-group-item d-flex justify-content-between align-items-center\">
                  <span>{{ u }}</span>
                  <div class=\"d-flex gap-2\">
                    <a class=\"btn btn-success btn-sm\" href=\"{{ url_for('resume', username=u) }}\">Genoptag</a>
                    <a class=\"btn btn-outline-danger btn-sm\" href=\"{{ url_for('reset_user', username=u) }}\" onclick=\"return confirm('Nulstil svar for ' + '{{ u }}' + '?');\">Nulstil</a>
                  </div>
                </li>
              {% endfor %}
            </ul>
          {% endif %}
        </div>
      </div>
    """
    inner = render_template_string(content, data=data, session=session, users_with_votes=users_with_votes)
    return render_template_string(base_layout, content=inner)


def _user_votes(data, username):
    return data["votes"].setdefault(username, {})


def _next_index_for_user(data, username):
    names = data.get("names", [])
    votes = data.get("votes", {}).get(username, {})
    # Find first name without a recorded yes/no vote
    for i, n in enumerate(names):
        if n not in votes:
            return i
    return len(names)


def _shuffled_order(names):
    # Return a shuffled list of indices for the provided names
    return random.sample(range(len(names)), k=len(names))


@app.route("/resume/<username>")
def resume(username):
    username = username.strip()
    if not username:
        return redirect(url_for("start"))
    data = load_data()
    if username not in data.get("votes", {}):
        # No saved votes, just start fresh
        session["username"] = username
        session.pop("idx", None)
        return redirect(url_for("swipe"))
    # Set session and index to next unanswered and redirect
    session["username"] = username
    # Create a shuffled order and position idx at first unanswered in this order
    order = _shuffled_order(data.get("names", []))
    session["order"] = order
    votes = data.get("votes", {}).get(username, {})
    next_idx = 0
    for i, idx in enumerate(order):
        name = data["names"][idx]
        if name not in votes:
            next_idx = i
            break
    else:
        next_idx = len(order)
    session["idx"] = next_idx
    return redirect(url_for("swipe"))


@app.route("/reset/<username>")
def reset_user(username):
    username = username.strip()
    if not username:
        return redirect(url_for("start"))
    data = load_data()
    # Remove user's votes if present
    if username in data.get("votes", {}):
        data["votes"].pop(username, None)
        save_data(data)
    # If resetting current session user, clear progress
    if session.get("username") == username:
        session.pop("idx", None)
    return redirect(url_for("start"))


@app.route("/swipe", methods=["GET", "POST"])
def swipe():
    username = session.get("username")
    if not username:
        return redirect(url_for("start"))
    data = load_data()
    votes = _user_votes(data, username)
    names = data["names"]
    # Ensure shuffled order exists for this run
    order = session.get("order")
    if order is None or len(order) != len(names):
        order = _shuffled_order(names)
        session["order"] = order
    if request.method == "POST":
        idx = int(request.form.get("idx", "0"))
        decision = request.form.get("decision")  # yes/no/skip
        # Comment removed
        if decision == "prev":
            # Go back without changing votes
            session["idx"] = max(idx - 1, 0)
            return redirect(url_for("swipe"))
        if 0 <= idx < len(order):
            name = names[order[idx]]
            if decision in ("yes", "no"):
                votes[name] = {"liked": decision == "yes"}
                data["votes"][username] = votes
                save_data(data)
        # Move to next
        next_idx = idx + 1
        if next_idx >= len(order):
            return redirect(url_for("results"))
        session["idx"] = next_idx
        return redirect(url_for("swipe"))

    idx = session.get("idx", 0)
    # Advance to the next unanswered name if current is already voted
    while idx < len(order) and names[order[idx]] in votes:
        idx += 1
    session["idx"] = idx
    if idx >= len(order):
        return redirect(url_for("results"))
    name = names[order[idx]]
    existing = votes.get(name)
    # Progress based on number of names already answered by this user
    answered_count = sum(1 for n in names if n in votes)
    content = """
      <div class=\"card\" style=\"max-width: 600px; margin: 0 auto;\">
        <h2 style=\"text-align:center;\">{{ name }}</h2>
        <form method=\"post\">
          <input type=\"hidden\" name=\"idx\" value=\"{{ idx }}\">
          <div class=\"actions\">
            <button id=\"noBtn\" class=\"no\" type=\"submit\" name=\"decision\" value=\"no\">Nej (←)</button>
            <div class=\"col-stack\">
              <button id=\"prevBtn\" class=\"undo\" type=\"submit\" name=\"decision\" value=\"prev\" data-bs-toggle=\"tooltip\" data-bs-placement=\"top\" title=\"Fortryd sidste trin (Pil op)\">Fortryd (↑)</button>
              <button id=\"skipBtn\" class=\"neutral\" type=\"submit\" name=\"decision\" value=\"skip\">Spring over (↓)</button>
            </div>
            <button id=\"yesBtn\" class=\"ok\" type=\"submit\" name=\"decision\" value=\"yes\">Ja (→)</button>
          </div>
          <p style=\"margin-top:0.5rem;color:#555;\">Tip: Højre pil = Ja, Venstre pil = Nej, Ned pil = Spring over, Op pil = Fortryd.</p>
        </form>
        <p>Fremskridt: {{ progress_current }} / {{ total }}</p>
      </div>
      <script>
        (function(){
          const yesBtn = document.getElementById('yesBtn');
          const noBtn = document.getElementById('noBtn');
          const skipBtn = document.getElementById('skipBtn');
          const prevBtn = document.getElementById('prevBtn');
          // Avoid triggering when typing in textarea
          function isTypingInTextArea(e) {
            const el = e.target;
            return el && (el.tagName === 'TEXTAREA' || (el.tagName === 'INPUT' && el.type === 'text'));
          }
          window.addEventListener('keydown', function(e){
            if (isTypingInTextArea(e)) return;
            if (e.key === 'ArrowRight' && yesBtn) { e.preventDefault(); yesBtn.click(); }
            else if (e.key === 'ArrowLeft' && noBtn) { e.preventDefault(); noBtn.click(); }
            else if (e.key === 'ArrowDown' && skipBtn) { e.preventDefault(); skipBtn.click(); }
            else if (e.key === 'ArrowUp' && prevBtn) { e.preventDefault(); prevBtn.click(); }
          });
          // Initialize Bootstrap tooltips
          if (window.bootstrap && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(function (tooltipTriggerEl) { new bootstrap.Tooltip(tooltipTriggerEl); });
          }
        })();
      </script>
    """
    inner = render_template_string(content, name=name, idx=idx, total=len(order), progress_current=answered_count + 1)
    return render_template_string(base_layout, content=inner)


@app.route("/results")
def results():
    data = load_data()
    names = data["names"]
    users = sorted(list(data["votes"].keys()))
    # Build per-name summary
    summary = []
    for n in names:
        record = {"name": n, "by": {}, "both": False, "liked_count": 0, "any_votes": False}
        likes = 0
        for u in users:
            v = data["votes"].get(u, {}).get(n)
            if v:
                record["by"][u] = v
                if v.get("liked"):
                    likes += 1
        record["both"] = likes >= 2 and len(users) >= 2
        record["liked_count"] = likes
        record["any_votes"] = len(record["by"]) > 0
        summary.append(record)
    # Sort: most liked first, then liked by both, then any votes (no votes last), then by name
    def sort_key(r):
        by_users = r["by"]
        liked_count = sum(1 for v in by_users.values() if v.get("liked"))
        return (-liked_count, -int(r["both"]), -int(r.get("any_votes", False)), r["name"].lower())
    summary.sort(key=sort_key)

    content = """
      <div class=\"d-flex justify-content-between align-items-center mb-3\">
        <h2 class=\"mb-0\">Resultater</h2>
        <a href=\"{{ url_for('add_names') }}\" class=\"btn btn-outline-primary\">Tilføj flere navne</a>
      </div>
      {% if not summary %}
        <div class=\"alert alert-warning\">Ingen navne endnu. Gå til Tilføj navne.</div>
      {% else %}
        <div class=\"table-responsive\">
          <table class=\"table table-striped table-bordered\">
            <thead class=\"table-light\">
              <tr>
                <th>Navn</th>
                {% for u in users %}<th>{{ u }} kunne lide?</th>{% endfor %}
                <th>Begge kunne lide?</th>
              </tr>
            </thead>
            <tbody>
              {% for r in summary %}
                {% set row_class = 'table-secondary' if not r.any_votes else ('table-success' if r.both else ('table-warning' if r.liked_count == 1 else 'table-danger')) %}
                <tr class=\"{{ row_class }}\">
                  <td><strong>{{ r.name }}</strong></td>
                  {% for u in users %}
                    {% set v = r.by.get(u) %}
                    <td>{% if v is not none %}{{ 'Ja' if v.liked else 'Nej' }}{% else %}-{% endif %}</td>
                  {% endfor %}
                  <td>{{ 'Ja' if r.both else 'Nej' }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% endif %}
    """
    inner = render_template_string(content, users=users, summary=summary)
    return render_template_string(base_layout, content=inner)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
