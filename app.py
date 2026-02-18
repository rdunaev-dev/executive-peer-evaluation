"""
Executive Peer Evaluation System
Система перекрёстной анонимной оценки топ-менеджеров

Features:
- Anonymous peer evaluation
- Voice input (Web Speech API)
- Quarterly assessment cycles
- Aggregated reports
"""

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, abort, jsonify, session
)
import os
from datetime import datetime, date
from models import (
    init_db, get_db, BLOCKS, ALL_QUESTIONS, SCORE_LABELS, MAX_SCORE, GRADE_LABELS,
    add_manager, get_managers, get_manager, update_manager, delete_manager,
    add_period, get_periods, get_period, activate_period, deactivate_period,
    get_tokens_for_period, get_token_data, get_evaluations_for_token,
    get_evaluation, save_evaluation,
    get_report_for_manager, get_period_completion_stats
)
from seed import auto_seed

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me-in-prod')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin2026')

init_db()
auto_seed(get_db)


# ─────────────────────────────────────────────
# Template context
# ─────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {
        "blocks": BLOCKS,
        "all_questions": ALL_QUESTIONS,
        "score_labels": SCORE_LABELS,
        "max_score": MAX_SCORE,
        "grade_labels": GRADE_LABELS,
        "now": datetime.now(),
    }


# ─────────────────────────────────────────────
# Home / Landing
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────
# Admin authentication
# ─────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Вы вошли в панель администратора", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Неверный пароль", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


def require_admin():
    if not session.get("is_admin"):
        abort(403)


# ─────────────────────────────────────────────
# Admin - Dashboard
# ─────────────────────────────────────────────

@app.route("/admin")
def admin_dashboard():
    require_admin()
    managers = get_managers()
    periods = get_periods()

    period_stats = {}
    for p in periods:
        period_stats[p['id']] = get_period_completion_stats(p['id'])

    return render_template("admin_dashboard.html",
                           managers=managers, periods=periods,
                           period_stats=period_stats)


# ─────────────────────────────────────────────
# Admin - Managers CRUD
# ─────────────────────────────────────────────

@app.route("/admin/managers/add", methods=["POST"])
def admin_add_manager():
    require_admin()
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    email = request.form.get("email", "").strip()
    if name and position:
        add_manager(name, position, email)
        flash(f"Руководитель {name} добавлен", "success")
    else:
        flash("Заполните имя и должность", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/managers/<int:manager_id>/edit", methods=["POST"])
def admin_edit_manager(manager_id):
    require_admin()
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    email = request.form.get("email", "").strip()
    if name and position:
        update_manager(manager_id, name, position, email)
        flash("Данные обновлены", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/managers/<int:manager_id>/delete", methods=["POST"])
def admin_delete_manager(manager_id):
    require_admin()
    delete_manager(manager_id)
    flash("Руководитель деактивирован", "success")
    return redirect(url_for("admin_dashboard"))


# ─────────────────────────────────────────────
# Admin - Periods
# ─────────────────────────────────────────────

@app.route("/admin/periods/add", methods=["POST"])
def admin_add_period():
    require_admin()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    if name and start_date and end_date:
        add_period(name, description, start_date, end_date)
        flash(f"Период «{name}» создан", "success")
    else:
        flash("Заполните все обязательные поля", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/periods/<int:period_id>/activate", methods=["POST"])
def admin_activate_period(period_id):
    require_admin()
    activate_period(period_id)
    flash("Период активирован, ссылки для оценки сгенерированы", "success")
    return redirect(url_for("admin_period_detail", period_id=period_id))


@app.route("/admin/periods/<int:period_id>/deactivate", methods=["POST"])
def admin_deactivate_period(period_id):
    require_admin()
    deactivate_period(period_id)
    flash("Период деактивирован", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/periods/<int:period_id>")
def admin_period_detail(period_id):
    require_admin()
    period = get_period(period_id)
    if not period:
        abort(404)
    tokens = get_tokens_for_period(period_id)
    stats = get_period_completion_stats(period_id)
    managers = get_managers()
    return render_template("admin_period.html",
                           period=period, tokens=tokens, stats=stats, managers=managers)


# ─────────────────────────────────────────────
# Admin - Reports
# ─────────────────────────────────────────────

@app.route("/admin/reports/<int:period_id>")
def admin_reports(period_id):
    require_admin()
    period = get_period(period_id)
    if not period:
        abort(404)
    managers = get_managers()
    stats = get_period_completion_stats(period_id)
    return render_template("admin_reports.html",
                           period=period, managers=managers, stats=stats)


@app.route("/admin/reports/<int:period_id>/manager/<int:manager_id>")
def admin_report_detail(period_id, manager_id):
    require_admin()
    period = get_period(period_id)
    manager = get_manager(manager_id)
    if not period or not manager:
        abort(404)
    report = get_report_for_manager(period_id, manager_id)
    return render_template("admin_report_detail.html",
                           period=period, manager=manager, report=report,
                           blocks=BLOCKS)


# ─────────────────────────────────────────────
# Evaluation - Public (anonymous via token)
# ─────────────────────────────────────────────

@app.route("/evaluate/<token>")
def evaluate_index(token):
    """Show list of colleagues to evaluate."""
    token_data = get_token_data(token)
    if not token_data:
        abort(404)
    if not token_data['period_active']:
        return render_template("evaluate_closed.html", token_data=token_data)

    evaluations = get_evaluations_for_token(token_data['id'])
    return render_template("evaluate_index.html",
                           token_data=token_data, evaluations=evaluations, token=token)


@app.route("/evaluate/<token>/person/<int:evaluation_id>", methods=["GET"])
def evaluate_form(token, evaluation_id):
    """Show evaluation form for a specific colleague."""
    token_data = get_token_data(token)
    if not token_data:
        abort(404)
    if not token_data['period_active']:
        return render_template("evaluate_closed.html", token_data=token_data)

    evaluation = get_evaluation(evaluation_id)
    if not evaluation or evaluation['token'] != token:
        abort(404)

    return render_template("evaluate_form.html",
                           token_data=token_data, evaluation=evaluation, token=token,
                           blocks=BLOCKS, score_labels=SCORE_LABELS)


@app.route("/evaluate/<token>/person/<int:evaluation_id>/save", methods=["POST"])
def evaluate_save(token, evaluation_id):
    """Save evaluation form data."""
    token_data = get_token_data(token)
    if not token_data:
        abort(404)

    evaluation = get_evaluation(evaluation_id)
    if not evaluation or evaluation['token'] != token:
        abort(404)

    # Collect scores and justifications
    scores_data = []
    for q in ALL_QUESTIONS:
        code = q['code']
        score_val = request.form.get(f"score_{code}", "")
        justification = request.form.get(f"justification_{code}", "").strip()

        score = int(score_val) if score_val else None

        scores_data.append({
            "question_code": code,
            "score": score,
            "justification": justification
        })

    advice = request.form.get("advice", "").strip()

    save_evaluation(evaluation_id, scores_data, advice)

    flash(f"Оценка для {evaluation['evaluatee_name']} сохранена!", "success")
    return redirect(url_for("evaluate_index", token=token))


# ─────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return redirect(url_for("admin_login"))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
