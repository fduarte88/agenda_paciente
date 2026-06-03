# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 6.0.3 web application for a speech therapy (fonoaudiología) clinic. Manages patients, weekly appointments, and system users. Language: Spanish (Colombian). Database: PostgreSQL. Python 3.14.

## Commands

```bash
# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Run tests for a single app
python manage.py test pacientes

# Collect static files (production)
python manage.py collectstatic
```

Environment variables for DB: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`. Defaults to `fonoapp_db` on localhost.

Production uses `fonoapp/settings_prod.py` (import via `DJANGO_SETTINGS_MODULE=fonoapp.settings_prod`).

## Architecture

### Apps

- **accounts** — Authentication (login/logout) and the dashboard home view. Uses Django's built-in `User`; no custom User model. Home aggregates stats from `pacientes` and `citas`.
- **pacientes** — `Paciente` model: name, birthdate, guardian info (name, phone, relationship). Includes computed `edad` property and birthday-of-the-month query in home.
- **citas** — `Cita` model: FK to `Paciente`, date, time slot, status (`pendiente`/`confirmada`/`cancelada`). The weekly agenda view builds a grid of 18 fixed 40-minute slots (08:00–19:20, Mon–Sat). Cancelled appointments free the slot for re-scheduling; the unique constraint excludes cancelled citas.
- **usuarios** — `Perfil` OneToOne extension of `User` with two roles (`admin`, `operador`) and 9 granular boolean permissions. Auto-created via `post_save` signal.

### Permission System

All non-public views require `@login_required` plus either `@permiso_requerido('permission_field_name')` or `@solo_admin` (defined in `usuarios/decorators.py`). Admins bypass all granular permission checks via `Perfil.tiene_permiso()`. Permissions are boolean fields on `Perfil`; `puede_ver_usuarios` and `puede_gestionar_usuarios` default to `False`.

### URL Structure

All apps are included at the root in `fonoapp/urls.py`:
- `/` and `/login/` — login
- `/home/` — dashboard
- `/pacientes/` — patient list/CRUD
- `/agenda/` — weekly schedule (navigate with `?semana=YYYY-MM-DD` Monday ISO date)
- `/usuarios/` — user management

### Templates & Static

Templates live in `templates/` at the project root (not per-app). `templates/base.html` is the shared layout. Static files are in `static/js/main.js`. Date inputs use a `dd/mm/YYYY` mask (class `date-mask`). All dates stored and displayed in `America/Bogota` timezone.

### Key Conventions

- Date input format site-wide: `dd/mm/YYYY` (forms accept both `%d/%m/%Y` and `%Y-%m-%d`).
- Appointment slot conflict validation is in `CitaForm.clean()` — only non-cancelled citas block a slot.
- The `Perfil` model must always exist for logged-in users; views catch missing profiles and redirect to home with an error.
