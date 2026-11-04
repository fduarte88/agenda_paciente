# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 6.0.3 web application for a speech therapy (fonoaudiología) clinic. Manages patients, weekly appointments, and system users. Language: Spanish (Colombian). Database: PostgreSQL. Python 3.14 locally, but production (`deploy/setup.sh`, EC2 Ubuntu 24.04) runs **Python 3.12** — keep code 3.12-compatible.

## Environment & Tests

`settings.py` loads `<repo>/.env` via python-dotenv (does not override vars already set). Vars: `SECRET_KEY`, `DEBUG`, `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` (defaults: `fonoapp_db`, `postgres`, localhost), `ALLOWED_HOSTS` (comma-separated, prod only).

`.env.example` is the **production** template: copying it locally sets `DEBUG=False`. Its `DJANGO_SETTINGS_MODULE=fonoapp.settings_prod` line only takes effect via gunicorn's `EnvironmentFile`; `manage.py` defaults to `fonoapp.settings`.

Tests: every `tests.py` is an empty stub, so `python manage.py test` runs 0 tests. It still requires PostgreSQL running (Django creates `test_fonoapp_db`).

## Architecture

### Apps

- **accounts** — Login/logout and the dashboard (`home_view`), which aggregates stats from `pacientes` and `citas`. Uses Django's built-in `User`; no custom User model.
- **pacientes** — `Paciente`: mother/father/tutor contacts, schooling, address, clinical history; computed `edad` property. `PacienteForm` title-cases name fields in `clean_*` methods — do the same for new name fields.
- **citas** — `Cita`: FK to `Paciente`, date, time slot (`HORARIOS`: 18 fixed 40-minute slots, 08:00–19:20, Mon–Sat), status (`pendiente`/`confirmada`/`cancelada`). Cancelling keeps the record and frees the slot. There is **no DB unique constraint** (migration 0002 dropped `unique_together`): double-booking is prevented only by `CitaForm.clean()` (non-cancelled citas block a slot), so anything that creates citas outside that form (admin, shell, new views) can double-book. When a slot has both a cancelled and an active cita, the agenda shows the active one.
- **usuarios** — `Perfil` OneToOne extension of `User` with two roles (`admin`, `operador`) and 9 granular boolean permissions. Auto-created via `post_save` signal.

### Permission System

All non-public views require `@login_required` plus either `@permiso_requerido('permission_field_name')` or `@solo_admin` (in `usuarios/decorators.py`). Admins bypass all granular checks via `Perfil.tiene_permiso()`. `puede_ver_usuarios` and `puede_gestionar_usuarios` default to `False`.

- `tiene_permiso()` uses `getattr(perfil, name, False)`: a misspelled permission name silently denies operators but still passes for admins. Test permission changes as an `operador`.
- `createsuperuser` gets a `Perfil` with `rol='operador'` (signal default) — a Django superuser is not an app admin until `rol='admin'` is set.
- Decorators redirect to `home` when a user has no profile, but `home_view` reads `request.user.perfil` unguarded and will crash.

### URLs

All app URLconfs are included at root with no prefix and no `app_name` namespaces — URL names are global (`redirect('home')`, not `'accounts:home'`). The agenda navigates with `?semana=YYYY-MM-DD` (the week's Monday).

### Templates, Static & Dates

Templates live in `templates/` at the project root (not per-app). Form templates render every `<input>` by hand (no `{{ form.field }}`), so adding a model/form field also requires editing the template HTML.

Date format site-wide is `dd/mm/aaaa`; timezone `America/Bogota`. The mask JS is **not** in `static/js/main.js` — each form template has its own inline `<script>` bound by element id (`id_fecha`, `id_fecha_nacimiento`). A new date field needs `forms.DateField(widget=forms.TextInput(attrs=DATE_WIDGET_ATTRS), input_formats=['%d/%m/%Y', '%Y-%m-%d'])` plus that inline script.

## Conventions

- Commit messages: one line, Spanish, 3rd-person present verb ("Agrega…", "Corrige…", "Mueve…").
- Migrations get descriptive Spanish names: `python manage.py makemigrations <app> --name reemplaza_x_por_y`.
- All UI text and `messages.*` strings are in Spanish.
- `main` is what `deploy/setup.sh` pulls onto the server (gunicorn systemd service `fonoapp` behind nginx).
