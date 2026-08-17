# Progressive Context Kit v1.7.0

**Token-Efficient · Quality-First · Spec-Driven**

> 🇬🇧 English version: [`README.md`](README.md) · подробный гайд: [`docs/human/GETTING_STARTED.ru.md`](docs/human/GETTING_STARTED.ru.md)

**Набор для Spec-Driven разработки с AI coding-агентами, ориентированный на качество и эффективное использование контекста.**

> **Минимизировать активный контекст, а не доступные знания.**

## С чего начать — для большинства пользователей

**Не копируй весь этот GitHub-репозиторий в свой проект.**

Этот репозиторий — **Framework Source**: исходники для разработки, тестирования и выпуска Progressive Context Kit.

Чтобы начать новый проект, скачай из GitHub Releases файл:

**`Progressive-Context-Project-Runtime-v1.7.0.zip`**

https://github.com/Elguajo/Progressive-Context-Spec-Kit/releases/latest

Project Runtime специально собран так, чтобы framework почти не был виден внутри реального проекта:

```text
my-project/
├── .agents/
├── .claude/
├── .progressive/
├── AGENTS.md
├── CLAUDE.md
└── <файлы самого продукта>
```

В корне проекта больше не появляются видимые framework-папки `global/`, `integrations/`, `profiles/`, `prompts/`, `templates/`, `tools/` и `docs/`.

Project Runtime по умолчанию использует **Standalone profile**. Поэтому новый пользователь может распаковать архив и сразу открыть Claude Code или Codex без предварительной настройки `~/.claude/CLAUDE.md` или `~/.codex/AGENTS.md`.

Первый prompt:

```text
Use .progressive/prompts/START_NEW_PROJECT.md.

My idea:
<опиши продукт, пользователей, реальные ограничения и явные non-goals>
```

## Один framework — две поверхности

```text
Progressive Context Kit — единый Framework Source
                        │
                        ├── Framework Source
                        │   GitHub repository
                        │   разработка / тесты / migration / release tooling
                        │
                        └── Project Runtime
                            GitHub Release asset
                            минимальный runtime для реальных проектов
```

Runtime **генерируется автоматически** из Framework Source. Это не два независимых Kit, поэтому их не нужно синхронизировать вручную.

## Когда нужен Framework Source

Этот GitHub-репозиторий нужен, если ты:

- развиваешь сам Progressive Context Kit;
- меняешь Skills, contracts, protocols или installer;
- поддерживаешь Claude/Codex adapters;
- работаешь с migration/evaluation evidence;
- запускаешь framework regression tests;
- собираешь новый Project Runtime release.

Human-only инструкция находится в `docs/human/GETTING_STARTED.md` (русская версия: `docs/human/GETTING_STARTED.ru.md`) и в Runtime не попадает.

## Сборка Project Runtime

```bash
python3 tools/build_release.py
```

Результат:

```text
dist/Progressive-Context-Project-Runtime-v1.7.0.zip
```

Старый `tools/build_starter.py` сохранён как compatibility alias, но начиная с v1.6 пользовательский пакет называется **Project Runtime**.

## Personal profile — опционально

Основной release сделан zero-setup через Standalone profile.

Если ты сознательно используешь Personal deployment на своей машине, Framework Source по-прежнему содержит:

- `global/AGENTS.codex.md` → `~/.codex/AGENTS.md`
- `global/CLAUDE.md` → `~/.claude/CLAUDE.md`

Установка в проект:

```bash
python3 tools/init_project.py /path/to/project --profile personal --agent both --dry-run
python3 tools/init_project.py /path/to/project --profile personal --agent both
```

Installer никогда сам не изменяет home-level agent configuration.

## Runtime context

Обычная работа идёт через:

```text
repository behavior
→ .progressive/project/PROJECT_BRIEF.md
→ .progressive/project/ARCHITECTURE.md
→ .progressive/project/ROADMAP.md
→ текущая .progressive/phases/*
→ компактный Completion Record предыдущей фазы
→ нужный Skill/protocol + релевантный код/тесты
```

Завершённые фазы, human docs, migration evidence и framework-development материалы не должны попадать в обычный warm-up.

## Проверка Framework Source

```bash
python3 tools/behavior_contract.py
python3 tools/framework_contract.py
python3 tools/duplication_audit.py
python3 tools/audit.py
python3 tools/build_runtime.py
python3 -m unittest discover -s tools/tests -v
```

## Проверка Project Runtime

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```
