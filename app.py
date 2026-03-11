"""
app.py — SGA ENSAE Dakar
Système de Gestion Académique
Réalisé par Gilbert OUMSAORE & Josée JEAZE — 3ème année ENSAE Dakar
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
from dash import html, dcc, Input, Output, State, callback, no_update

from models.database import init_db
from utils.migration import seed_demo_data
from utils.layout import build_navbar, build_footer, CUSTOM_CSS, EXTERNAL_CSS, C

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
seed_demo_data()

# ── IMPORT OBLIGATOIRE de tous les modules au démarrage ───────────────────────
import pages.login
import pages.accueil
import pages.dashboard
import pages.cours
import pages.seances
import pages.etudiants
import pages.notes
import pages.analytics
import pages.apropos
import pages.migration

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=EXTERNAL_CSS,
    suppress_callback_exceptions=True,
    title="SGA — ENSAE Dakar",
    update_title=None,
)
server = app.server  # nécessaire pour gunicorn

app.index_string = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
{CUSTOM_CSS}
    </style>
</head>
<body>
    {{%app_entry%}}
    <footer>
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </footer>
</body>
</html>
"""

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="auth-store", storage_type="session", data=None),
    html.Div(id="navbar-container"),
    html.Div(id="page-content"),
    html.Div(id="footer-container"),
])

ROUTES = {
    "/":          pages.accueil,
    "/accueil":   pages.accueil,
    "/dashboard": pages.dashboard,
    "/cours":     pages.cours,
    "/seances":   pages.seances,
    "/etudiants": pages.etudiants,
    "/notes":     pages.notes,
    "/analytics": pages.analytics,
    "/apropos":   pages.apropos,
    "/migration": pages.migration,
}

USERS = {
    "admin":   "ensae2025",
    "gilbert": "sga2025",
    "josee":   "sga2025",
    "prof":    "dataviz25",
}


@callback(
    Output("page-content",     "children"),
    Output("navbar-container", "children"),
    Output("footer-container", "children"),
    Input("url",               "pathname"),
    State("auth-store",        "data"),
)
def display_page(pathname, auth):
    pathname = pathname or "/"
    if pathname == "/login":
        return pages.login.layout(), None, None
    if not (auth and auth.get("logged_in")):
        return pages.login.layout(), None, None

    navbar = build_navbar()
    footer = build_footer()
    mod    = ROUTES.get(pathname)

    if mod is None:
        return (html.Div(className="page-wrapper", children=[
            html.Div(className="page-content", children=[
                html.Div(style={"textAlign":"center","paddingTop":"80px"}, children=[
                    html.Div("404", style={"fontFamily":"'Merriweather',serif",
                                           "fontSize":"96px","fontWeight":"900","color":C["bleu_pale2"]}),
                    html.Div("Page introuvable", style={"fontSize":"22px","color":C["muted"],"marginBottom":"20px"}),
                    dcc.Link("← Retour à l'accueil", href="/", className="btn-bleu"),
                ]),
            ]),
        ]), navbar, footer)

    if pathname in ("/", "/accueil"):
        return html.Div(className="page-wrapper", children=[mod.layout()]), navbar, footer

    try:
        content = html.Div(className="page-wrapper", children=[
            html.Div(className="page-content", children=[mod.layout()]),
        ])
    except Exception as e:
        content = html.Div(className="page-wrapper", children=[
            html.Div(className="page-content", children=[
                html.Div(f"Erreur : {e}",
                         style={"color":C["danger"],"padding":"24px","background":"#FFF5F5",
                                "borderRadius":"10px","fontFamily":"'Fira Code',monospace",
                                "border":"1px solid #FFCDD2"}),
            ]),
        ])
    return content, navbar, footer


@callback(
    Output("url",            "pathname", allow_duplicate=True),
    Output("auth-store",     "data",     allow_duplicate=True),
    Output("login-feedback", "children"),
    Input("login-btn",       "n_clicks"),
    Input("login-pass",      "n_submit"),
    State("login-user",      "value"),
    State("login-pass",      "value"),
    prevent_initial_call=True,
)
def do_login(n_btn, n_submit, username, password):
    if not username or not password:
        return no_update, no_update, html.Div(
            "Identifiant et mot de passe requis.", className="alert-sga",
            style={"background":"#FFF3E0","color":C["warning"],"borderLeftColor":C["warning"]})
    if USERS.get(username) == password:
        return "/", {"logged_in":True,"user":username}, html.Div(
            f"Bienvenue, {username} !", className="alert-sga",
            style={"background":"#E8F5E9","color":C["success"],"borderLeftColor":C["success"]})
    return no_update, no_update, html.Div(
        "Identifiant ou mot de passe incorrect.", className="alert-sga",
        style={"background":"#FFEBEE","color":C["danger"],"borderLeftColor":C["danger"]})


if __name__ == "__main__":
    print("\n" + "="*58)
    print("  SGA ENSAE Dakar — Système de Gestion Académique")
    print("  Réalisé par : Gilbert OUMSAORE & Josée JEAZE")
    print("  Élèves Analystes Statisticiens — 3ème année")
    print("  URL  : http://localhost:8050")
    print("  Comptes : admin/ensae2025  |  gilbert/sga2025")
    print("="*58 + "\n")


    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)