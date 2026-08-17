# Progressive Context Spec Kit — Быстрый старт

> **Гайд только для человека.** Этот файл принадлежит Framework Source и намеренно исключён из релиза Project Runtime — агент не должен читать его как обычный context.
>
> English version: [`GETTING_STARTED.md`](GETTING_STARTED.md)

## 0. Зачем это нужно

Когда AI-агент работает с проектом без дополнительной системы, ему часто приходится заново выяснять: что это за продукт, какая у него архитектура, что уже сделано, что делать следующим, какие решения уже приняты, какие ограничения нельзя нарушать, какие тесты запускать и где закончилась предыдущая сессия.

На маленьком проекте это терпимо. На долгом проекте это превращается в повторное чтение файлов, разрастающиеся prompts и риск того, что новая сессия примет решения, противоречащие предыдущим.

Progressive Context хранит состояние проекта отдельно от чата:

```text
Идея продукта
      ↓
Project Brief
      ↓
Architecture
      ↓
Roadmap
      ↓
текущая Phase
      ↓
реализация
      ↓
проверка
      ↓
Completion Record / Handoff
      ↓
Next Session
```

Северная звезда дизайна: **минимизировать активный контекст, а не доступные знания.** Ничего не удаляется — просто не всё грузится в каждую сессию.

## 1. Рекомендуемый путь: скачать Project Runtime

Для обычной продуктовой работы не клонируй и не копируй весь репозиторий Framework Source.

Скачай последний release asset:

```text
Progressive-Context-Project-Runtime-v1.7.0.zip
```

со страницы:

```text
https://github.com/Elguajo/Progressive-Context-Spec-Kit/releases/latest
```

Распакуй его в директорию, которая станет твоим проектом.

Начальная поверхность framework должна выглядеть так:

```text
my-project/
├── .agents/
├── .claude/
├── .progressive/
├── AGENTS.md
└── CLAUDE.md
```

Всё, что относится к Progressive и не обязано быть нативной agent-точкой входа, живёт в скрытой директории `.progressive/`. Видимых framework-папок вроде `global/`, `integrations/`, `profiles/`, `prompts/`, `templates/`, `tools/` или `docs/` в корне продукта не будет.

## 2. Глобальная настройка не обязательна

Основной релиз Project Runtime использует **Standalone profile**.

Это значит, что перед началом работы не нужно ничего устанавливать в:

```text
~/.claude/CLAUDE.md
~/.codex/AGENTS.md
```

Это осознанное решение: основной download должен работать с минимальным количеством шагов настройки и минимальной неоднозначностью установки.

## 3. Запусти Claude Code или Codex

Пример с Claude Code:

```bash
cd /path/to/my-project
git init   # если нужно
claude
```

Project-level Claude Skills остаются в:

```text
.claude/skills/
```

Не копируй их в user-level `~/.claude/skills/` в рамках обычной установки Project Runtime.

## 4. Первый prompt

Для нового продукта:

```text
Use .progressive/prompts/START_NEW_PROJECT.md.

My idea:
<опиши проблему, целевых пользователей, желаемый результат, реальные ограничения и явные non-goals>
```

Описывай в первую очередь **что** ты хочешь получить и реальные ограничения.

Не выбирай заранее framework, базу данных, hosting, state management или структуру директорий, если это не настоящее продуктовое/организационное требование. Workflow сам должен определить подходящий scope, архитектуру, roadmap, фазы реализации и стратегию проверки.

## 5. Что Progressive должен поддерживать

```text
Идея
→ Project Brief
→ Architecture
→ Roadmap
→ текущая Phase
→ Реализация
→ Проверка
→ Completion Record / Handoff
→ Next Session
```

Владельцы состояния в Runtime:

- `.progressive/project/PROJECT_BRIEF.md` — истина о продукте;
- `.progressive/project/ARCHITECTURE.md` — текущая истина о системе;
- `.progressive/project/ROADMAP.md` — канонический порядок/статус фаз;
- `.progressive/phases/*` — контракты реализации и acceptance criteria;
- `Completion Record` завершённой фазы — компактный устойчивый мост между фазами;
- `.progressive/project/NEXT_SESSION.md` — перезаписываемая горячая навигация;
- `.progressive/decisions/*` — консequential rationale, когда ADR оправдан.

Тебе не нужно вручную указывать агенту, какие из этих файлов поддерживать в актуальном состоянии — это часть workflow.

## 6. Продолжение работы между сессиями

После значимой сессии:

1. дай агенту провалидировать результат и подготовить handoff;
2. полностью закрой сессию;
3. открой новую сессию в том же репозитории;
4. вставь только сгенерированный `NEXT SESSION PROMPT`;
5. не пересказывай проект заново вручную, если только что-то действительно важное не потерялось.

Это практический тест непрерывности, который Progressive должен проходить.

Для новой сессии можно также использовать:

```text
Use .progressive/prompts/CONTINUE_PROJECT.md and continue autonomously.
```

## 7. Что агент должен читать по умолчанию

Для обычной продуктовой работы предпочтителен минимально достаточный context:

```text
repository behavior
+ Project Brief
+ Architecture
+ Roadmap
+ текущая Phase
+ Completion Record непосредственно предыдущей фазы (когда релевантно)
+ релевантный код/тесты по задаче
+ подходящий Skill/protocol
```

Агент не должен рекурсивно прогреваться из всей директории `.progressive/`. Human-документы, migration evidence, framework-тесты, полные тела завершённых фаз и история framework намеренно отсутствуют в пакете Runtime.

## 8. Проверка Runtime

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

Runtime audit проверяет только целостность проекта/runtime. Полные behavior/framework contracts остаются в Framework Source.

## 9. Personal deployment — опциональный продвинутый режим

Personal-режим по-прежнему поддерживается для тех, кто осознанно хочет один user-global слой инженерных правил, общий для многих репозиториев.

Из доверенной копии Framework Source:

Claude Code:

```text
global/CLAUDE.md → ~/.claude/CLAUDE.md
```

Codex:

```text
global/AGENTS.codex.md → ~/.codex/AGENTS.md
```

Затем установка в проект:

```bash
python3 tools/init_project.py /path/to/project --profile personal --agent both --dry-run
python3 tools/init_project.py /path/to/project --profile personal --agent both
```

Не добавляй поверх Personal-глобальных инструкций Progressive старый длинный custom instructions prompt, если только не хочешь намеренно продублировать поведение.

Installer никогда сам не изменяет home-level agent configuration.

## 10. Существующие проекты

Adoption остаётся операцией Framework Source, потому что требует reconciliation/update tooling, а не только финальный Runtime payload:

```bash
python3 tools/init_project.py /path/to/existing-project --profile standalone --adopt-existing --dry-run
python3 tools/init_project.py /path/to/existing-project --profile standalone --adopt-existing
```

Дай агенту:

```text
Use prompts/ADOPT_EXISTING_PROJECT.md.

Adopt Progressive Context Spec Kit into this existing repository.
Do not treat this as a blank project.

First understand the product and architecture that actually exist from repository evidence.
Preserve existing code, documentation, Git changes and project-specific instructions.

Reconstruct the canonical project state: PROJECT_BRIEF, ARCHITECTURE, ROADMAP, current PHASE.
Separate already-completed capabilities from future work.
Reconcile existing AGENTS.md / CLAUDE.md and documentation instead of blindly replacing them.
```

Агент не должен придумывать новую архитектуру и описывать её так, будто она уже существует. Сначала — исследование фактического состояния, отдельно — желаемые будущие изменения.

## 11. Если ты развиваешь сам Progressive Context

Клонируй репозиторий Framework Source вместо релиза Project Runtime.

Framework Source намеренно содержит видимые directories для разработки:

```text
global/
integrations/
profiles/
prompts/
templates/
tools/
docs/
```

Эти файлы существуют для разработки и проверки Progressive; их не нужно копировать целиком в продуктовые репозитории.

Сборка нового Project Runtime:

```bash
python3 tools/build_release.py
```

Результат:

```text
dist/Progressive-Context-Project-Runtime-v1.7.0.zip
dist/Progressive-Context-Project-Runtime-v1.7.0.manifest.json
dist/SHA256SUMS.txt
```

`tools/build_release.py` — канонический release entrypoint: проверяет Framework Source, собирает Runtime, аудирует распакованный Runtime и пишет release metadata. `tools/build_runtime.py` — более низкоуровневый шаг упаковки. `tools/build_starter.py` сохранён как compatibility alias, но с v1.6 пользовательский пакет называется **Project Runtime**.

Проверка Framework Source:

```bash
python3 tools/behavior_contract.py
python3 tools/framework_contract.py
python3 tools/duplication_audit.py
python3 tools/audit.py
python3 tools/build_runtime.py
python3 -m unittest discover -s tools/tests -v
```

## 12. Как пользоваться каждый день

После первоначального bootstrap не нужно каждый раз пересказывать агенту всю историю проекта.

**Исправить ошибку:**

```text
Use .progressive/prompts/BUG_FIX.md.

Problem:
<опиши, что сломалось и что ты наблюдаешь>
```

**Добавить новую возможность или изменить существующую:**

```text
Use .progressive/prompts/CHANGE_REQUEST.md.

Change:
<что ты хочешь изменить>
```

**Провести code review:**

```text
Use .progressive/prompts/REVIEW.md.

Review the current implementation/change.
Prioritize only meaningful correctness, security, regression and maintainability findings.
```

**Настроить tooling:**

```text
Use .progressive/prompts/SETUP_TOOLING.md.
Inspect the current project and tooling status.
Recommend and configure only tools that materially improve this project.
```

> Если ты работаешь из клона Framework Source (не из скачанного Runtime), пути к этим prompts — `prompts/...` без префикса `.progressive/`.

## 13. Как работают Skills

В Spec Kit есть специализированные workflow-Skills:

| Skill | Когда подключается |
|---|---|
| `project-bootstrap` | инициализация нового продукта |
| `existing-project-adoption` | adoption существующего репозитория |
| `tooling-bootstrap` | отсутствует материально полезный preferred tool |
| `implementation-execution` | нетривиальная реализация после согласованного направления |
| `architecture-decision` | материальный архитектурный/технологический выбор |
| `security-sensitive-change` | auth/payments/permissions/secrets/private data/untrusted input/SQL/CSRF/redirects/webhooks/migrations |
| `systematic-debugging` | неясная/нестабильная/stateful первопричина |
| `code-review` | ревью кода/diff/PR или вставленный код без конкретного вопроса |
| `documentation-governance` | материальное изменение durable governance-документации |
| `session-handoff` | завершение значимой сессии реализации/ревью |
| `project-doctor` | неясное/противоречивое состояние проекта |
| `workflow-audit` | проверка целостности самого Progressive Context |

Главное правило:

> **Установленный Skill ≠ Skill загружается в каждую сессию.**

Например, обычное изменение текста на кнопке не должно подключать `security-sensitive-change` или `architecture-decision`. Но задача про payment integration может подключить `security-sensitive-change` + `implementation-execution` + релевантный project context одновременно.

## 14. Рекомендуемые инструменты

Progressive Context не пытается заменить сильные специализированные инструменты. Recommended-профиль явно знает о следующих:

| Инструмент | Для чего |
|---|---|
| **Semble** | поиск логики по смыслу (intent/semantic discovery) в большом codebase |
| **Serena** | symbols, references, implementations, безопасный refactor по известным символам |
| **RTK** | более компактный вывод terminal/test/build/git |
| **Superpowers** | дисциплина implementation/TDD/debugging |
| **gstack** | challenge/review/browser QA/release checks |
| **Context7** | актуальная документация библиотек и API |
| **GitHub Spec Kit** | опциональный Advanced Spec Mode — глубокая формальная specification для сложных/high-risk фаз |

Если полезный инструмент отсутствует, агент не должен просто делать вид, что его нет:

```text
нужна capability
      ↓
preferred tool установлен?
      ↓
да → использовать
нет
      ↓
инструмент действительно даст заметную пользу?
      ↓
да → предложить установку/подключение (Skill tooling-bootstrap)
нет → продолжить native средствами
```

Мелкая задача не должна блокироваться только ради установки дополнительного инструмента. Installed ≠ loaded ≠ invoked — сам факт установки не означает, что инструмент подключается в каждой сессии.

## 15. Проверка установки

Для Project Runtime, из корня распакованного проекта:

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

Для Framework Source, из корня этого репозитория:

```bash
python3 tools/audit.py
python3 tools/behavior_contract.py
python3 tools/framework_contract.py
python3 tools/duplication_audit.py
python3 -m unittest discover -s tools/tests -v
```

Для ежедневной разработки не нужно вручную запускать весь набор Framework Source после каждой маленькой задачи — это проверки самого framework, а не обычная продуктовая работа.

## 16. Частые вопросы

**Нужно ли устанавливать Progressive отдельно для Codex и Claude?**
Нет. Один и тот же Project Runtime (или один repository router `AGENTS.md` для Framework Source) обслуживает Codex, Claude Code или оба сразу — выбор делается флагом `--agent` при сборке/установке.

**Нужно ли копировать global instructions в каждый проект?**
Нет. В режиме Personal они устанавливаются один раз (`~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`). Основной релиз Project Runtime вообще не требует global-настройки — он самодостаточен через Standalone profile.

**Все Skills постоянно расходуют токены?**
Нет. Они предназначены для progressive/on-demand loading. Сам факт наличия Skill в проекте не означает, что всё его содержимое попадает в каждую сессию.

**Human-документы вроде этого гайда будут постоянно читаться агентом?**
Нет. `docs/human/` (Framework Source) намеренно исключена из сборки Project Runtime и не входит в обычный warm-up context.

**Что делать, если в существующем проекте уже есть `AGENTS.md`?**
Использовать `--adopt-existing`. Не заменяй существующий файл вслепую — adoption workflow должен сохранить project-specific инструкции и согласовать их с framework router.

**Чем Framework Source отличается от Project Runtime?**
Framework Source — это GitHub-репозиторий для разработки, тестирования и релиза самого Progressive Context. Project Runtime — сгенерированный из него release asset, минимальный и в основном скрытый (`.progressive/`), который распаковывается прямо в продуктовый проект. Runtime генерируется автоматически из Framework Source, поэтому это не два независимых Spec Kit, которые нужно синхронизировать вручную.

## 17. Как понять, что всё работает правильно

После хорошей настройки ожидаемое поведение выглядит так:

```text
Ты открываешь новую AI-сессию
        ↓
пишешь коротко: "Continue the project"
        ↓
agent восстанавливает Project Brief / Architecture / Roadmap / текущую Phase
        ↓
не перечитывает весь проект без причины
        ↓
подключает нужный Skill/tool только при реальной необходимости
        ↓
реализует изменение
        ↓
проверяет результат
        ↓
обновляет состояние (Completion Record, Roadmap, NEXT_SESSION)
        ↓
готовит следующую сессию
```

Тебе не нужно каждый раз писать огромный prompt и вручную пересказывать AI, что происходило в предыдущих сессиях.

## 18. Главное правило

Используй Progressive как workflow, а не как ещё одну коллекцию prompts, которую нужно вручную поддерживать.

Пользователь владеет желаемым результатом и реальными решениями. Агент владеет context routing, состоянием проекта, реализацией, проверкой и непрерывностью между сессиями.
