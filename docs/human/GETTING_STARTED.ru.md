# Progressive Context Kit — Быстрый старт

> **Гайд только для человека.** Этот файл принадлежит Framework Source и намеренно исключён из Project Runtime.
>
> English version: [`GETTING_STARTED.md`](GETTING_STARTED.md)

**Token-Efficient · Quality-First · Spec-Driven**

Если хочешь сначала понять идею, а не команды:

- [`Глоссарий и терминология`](GLOSSARY.ru.md)
- [`Как работает Progressive Context`](HOW_PROGRESSIVE_CONTEXT_WORKS.ru.md)
- [`Модель памяти проекта`](PROJECT_MEMORY_MODEL.ru.md)
- [`Безопасное обновление Project Runtime`](UPDATING_RUNTIME.ru.md)
- [`Визуальный onboarding`](../visuals/user-onboarding.md)

## 1. Скачай Project Runtime

Для обычной продуктовой работы **не клонируй и не копируй весь Framework Source**.

Скачай последний release asset:

```text
Progressive-Context-Project-Runtime-v1.8.0.zip
```

со страницы GitHub Releases:

```text
https://github.com/Elguajo/Progressive-Context-Kit/releases/latest
```

Распакуй архив в директорию будущего проекта.

Начальная поверхность должна выглядеть так:

```text
my-project/
├── .agents/
├── .claude/
├── .progressive/
├── AGENTS.md
└── CLAUDE.md
```

Всё Progressive-специфичное, что не обязано быть нативной точкой входа агента, живёт внутри скрытой `.progressive/`.

## 2. Глобальная настройка для основного релиза не нужна

Основной Project Runtime использует **Standalone profile**.

Перед началом работы не нужно ничего устанавливать в:

```text
~/.claude/CLAUDE.md
~/.codex/AGENTS.md
```

Это специально сделано так, чтобы основной download был zero-setup.

## 3. Запусти Claude Code или Codex

Например:

```bash
cd /path/to/my-project
git init   # если нужно
claude
```

Project-level Claude Skills остаются в:

```text
.claude/skills/
```

Не копируй их в `~/.claude/skills/` как часть обычной установки Runtime.

## 4. Первый prompt

Для нового продукта:

```text
Use .progressive/prompts/START_NEW_PROJECT.md.

My idea:
<опиши проблему, пользователей, желаемый результат, реальные ограничения и явные non-goals>
```

Описывай прежде всего **что** нужно получить и реальные ограничения.

Не выбирай заранее framework, database, hosting, state management или структуру директорий, если это не настоящее продуктовое или организационное требование. Workflow должен сам определить подходящий scope, архитектуру, Roadmap, phases и validation strategy.

## 5. Что Progressive поддерживает в актуальном состоянии

```text
Идея
→ PROJECT_BRIEF
→ ARCHITECTURE
→ ROADMAP
→ Current Phase
→ Implementation
→ Verification
→ Phase Completion Report + compact Completion Record
→ Next Phase / NEXT_SESSION
```

Основные владельцы состояния:

- `.progressive/project/PROJECT_BRIEF.md` — продуктовая истина;
- `.progressive/project/ARCHITECTURE.md` — текущая истина о системе;
- `.progressive/project/ROADMAP.md` — порядок и статус phases;
- `.progressive/phases/*` — execution + acceptance contracts;
- `.progressive/completions/*` — подробная долговременная история завершённых phases, читаемая on demand;
- `Completion Record` завершённой Phase — компактный мост между фазами;
- `.progressive/project/NEXT_SESSION.md` — перезаписываемая hot navigation;
- `.progressive/decisions/*` — consequential rationale, когда нужен ADR.

Подробно: [`Модель памяти проекта`](PROJECT_MEMORY_MODEL.ru.md).

## 6. Продолжение между сессиями

После значимой сессии:

1. дай агенту провалидировать результат и подготовить handoff;
2. полностью закрой сессию;
3. открой новую в том же репозитории;
4. вставь только сгенерированный `NEXT SESSION PROMPT`;
5. не пересказывай весь проект вручную, если что-то действительно не потерялось.

Можно также использовать:

```text
Use .progressive/prompts/CONTINUE_PROJECT.md and continue autonomously.
```

Визуальный flow: [`session-context-flow.md`](../visuals/session-context-flow.md).

## 7. Что агент должен читать по умолчанию

Минимально достаточный context:

```text
repository behavior
+ Project Brief
+ Architecture
+ Roadmap
+ текущая Phase
+ предыдущий compact Completion Record, когда нужен
+ релевантный код/тесты
+ подходящий Skill/protocol
```

Агент не должен рекурсивно прогреваться из всей `.progressive/`.

Human docs, visual explanations, migration evidence, framework tests, полные старые phases и подробные completion reports не должны попадать в обычный warm-up.

## 8. Проверка Runtime

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

Runtime audit проверяет целостность проекта/runtime. Полные behavior/framework contracts остаются во Framework Source.

## 9. Ежедневные задачи

### Исправить ошибку

```text
Use .progressive/prompts/BUG_FIX.md.

Problem:
<что сломалось и что наблюдаешь>
```

### Добавить или изменить возможность

```text
Use .progressive/prompts/CHANGE_REQUEST.md.

Change:
<что нужно изменить>
```

### Провести review

```text
Use .progressive/prompts/REVIEW.md.

Review the current implementation/change.
Prioritize only meaningful correctness, security, regression and maintainability findings.
```

### Настроить tooling

```text
Use .progressive/prompts/SETUP_TOOLING.md.
Inspect the current project and tooling status.
Recommend and configure only tools that materially improve this project.
```

## 10. Как работают Skills

Главное правило:

> **Installed ≠ loaded ≠ invoked.**

Наличие Skill не означает, что он загружается в каждую сессию.

Примеры routing:

- implementation → `implementation-execution`;
- неясная root cause → `systematic-debugging`;
- architecture choice → `architecture-decision`;
- auth/payments/secrets/permissions и другие sensitive changes → `security-sensitive-change`;
- review → `code-review`;
- meaningful handoff → `session-handoff`.

Визуально: [`tool-routing.md`](../visuals/tool-routing.md).

## 11. Existing project

Adoption требует Framework Source tooling:

```bash
python3 tools/init_project.py /path/to/existing-project --profile standalone --adopt-existing --dry-run
python3 tools/init_project.py /path/to/existing-project --profile standalone --adopt-existing
```

Не относись к существующему репозиторию как к blank project. Сначала восстанови фактический product/system state из evidence, затем уже планируй будущее.

## 12. Обновление Runtime

Не распаковывай новый ZIP вслепую поверх важного проекта.

Предпочтительный путь из доверенного Framework Source checkout:

```bash
python3 tools/init_project.py /path/to/project --update-framework --dry-run
python3 tools/init_project.py /path/to/project --update-framework
```

Подробно: [`Безопасное обновление Project Runtime`](UPDATING_RUNTIME.ru.md).

## 13. Personal deployment — опционально

Если сознательно нужен user-global engineering layer для многих репозиториев:

```text
global/CLAUDE.md → ~/.claude/CLAUDE.md
global/AGENTS.codex.md → ~/.codex/AGENTS.md
```

Затем:

```bash
python3 tools/init_project.py /path/to/project --profile personal --agent both --dry-run
python3 tools/init_project.py /path/to/project --profile personal --agent both
```

Installer сам не меняет home-level agent configuration.

## 14. Если ты развиваешь Progressive Context Kit

Тогда нужен именно Framework Source, а не Runtime ZIP.

Framework Source содержит:

```text
global/
integrations/
profiles/
prompts/
templates/
tools/
docs/
```

Сборка Project Runtime:

```bash
python3 tools/build_release.py
```

Результат:

```text
dist/Progressive-Context-Project-Runtime-v1.8.0.zip
dist/Progressive-Context-Project-Runtime-v1.8.0.manifest.json
dist/SHA256SUMS.txt
```

Проверка Framework Source:

```bash
python3 tools/behavior_contract.py
python3 tools/framework_contract.py
python3 tools/duplication_audit.py
python3 tools/audit.py
python3 tools/build_runtime.py
python3 -m unittest discover -s tools/tests -v
```

Human-only схемы находятся в [`docs/visuals/`](../visuals/README.md) и намеренно не попадают в Runtime.

## 15. Главное правило

Используй Progressive Context Kit как workflow, а не как коллекцию prompts, которую нужно вручную поддерживать.

Пользователь в первую очередь владеет желаемым результатом и реальными решениями. Агент владеет context routing, состоянием проекта, реализацией, проверкой и continuity между сессиями.
