# Progressive Context Kit — Глоссарий

> **Справочник только для человека.** Этот файл принадлежит Framework Source и намеренно исключён из Project Runtime.
>
> English version: [`GLOSSARY.md`](GLOSSARY.md)

Используй эту страницу, если непонятен термин framework, сокращение, identifier или элемент модели project memory.

## Как писать термины

В human-facing документации при первом упоминании лучше писать полное название, а сокращение добавлять в скобках только если оно действительно будет использоваться дальше.

Хорошо:

```text
Architecture Decision Record (ADR)
Default Read Set (DRS)
Phase Completion Report (PCR)
```

Плохо:

```text
NSP должен сохранять семантику DRS после PCR.
```

Стабильные identifiers вроде `PC-012`, символы кода, имена файлов, CLI flags и короткие подписи на схемах могут оставаться сокращёнными.

## Сокращения Progressive Context Kit

| Сокращение | Расшифровка | Как используется |
|---|---|---|
| **PC** | Progressive Context | Формально используется в IDs защищённых invariants: например `PC-001` и `PC-012`. |
| **FW** | Framework | Неформальное сокращение. В human docs лучше писать **Framework** полностью. |
| **FS** | Framework Source | Неформальное сокращение. Обычно лучше писать полное название. |
| **DRS** | Default Read Set | Минимальный стандартный набор project state, с которого начинается восстановление context перед on-demand расширением. |
| **CR** | Completion Record | Компактный durable bridge внутри завершённой Phase. В обычном тексте лучше писать полное название. |
| **PCR** | Phase Completion Report | Подробная долговременная история одной завершённой Phase; относится к cold/on-demand context. |
| **NS** | `NEXT_SESSION` | Неформальное сокращение для volatile hot continuation state. Лучше использовать имя файла или полное название. |
| **NSP** | `NEXT_SESSION_PROMPT` | Неформальное сокращение для готового single-focus prompt следующей сессии. Лучше писать полное название. |

Эти сокращения не нужны для работы с Kit. Они нужны прежде всего для понимания implementation notes, issues, PR discussions, diagrams и invariant IDs.

## Общие инженерные сокращения

| Сокращение | Расшифровка | Значение в проекте |
|---|---|---|
| **ADR** | Architecture Decision Record | Фиксирует одно важное архитектурное решение и его rationale. |
| **AC** | Acceptance Criteria | Условия, которые должны быть выполнены до того, как Task или Phase считается завершённой. |
| **PR** | Pull Request | Предложение изменений в GitHub перед merge. |
| **CI** | Continuous Integration | Автоматические проверки: contracts, audits, builds, tests и другие gates. |
| **QA** | Quality Assurance | Проверка корректности и user-visible поведения, включая ручную verification, когда она нужна. |
| **CLI** | Command-Line Interface | Работа через команды, например `python3 tools/build_release.py`. |
| **API** | Application Programming Interface | Программный интерфейс между компонентами или сервисами. |
| **SHA / SHA-256** | Secure Hash Algorithm / SHA-256 | Используется для commit identifiers и проверки целостности release artifacts. |
| **TDD** | Test-Driven Development | Подход, при котором tests направляют изменение поведения, когда это уместно. |

## Основные термины framework

### Framework Source

Канонический GitHub-репозиторий, в котором разрабатывается, тестируется, документируется и выпускается сам Progressive Context Kit.

Он содержит framework-development материалы: `docs/`, `templates/`, `tools/`, contracts, tests, profiles и release tooling.

### Project Runtime

Сгенерированный минимальный пакет, который помещается в реальный продуктовый репозиторий.

Он содержит operational machinery Progressive Context, нужную агенту, но намеренно не включает human documentation и development-материалы Framework Source.

### Project-owned

Состояние, принадлежащее реальному продукту и которое должно сохраняться при обновлении framework. Например: project memory, phases, completion reports, decisions, application code и project-specific instructions.

### Framework-owned

Runtime machinery, генерируемая из Framework Source и обновляемая вместе с framework при соблюдении правил сохранения project-owned state.

### Canonical owner / source of truth

Один документ или artifact, который отвечает за конкретный durable факт или правило. Другие файлы могут его кратко объяснять или ссылаться на него, но не должны становиться конкурирующим source of truth.

### Default Read Set

Минимальный стандартный context, с которого агент восстанавливает состояние проекта до загрузки дополнительного материала. Точная operational routing задаётся framework; принцип — начать с малого и расширять context только когда этого требует evidence.

### Hot context

Информация, которая нужна прямо сейчас для текущего continuation: текущее состояние и ближайший незакрытый execution target.

### Cold / on-demand context

Доступные знания, которые не должны загружаться в обычный warm-up без необходимости investigation, audit, history или evidence. Подробные Phase Completion Reports — пример такого слоя.

### Always-loaded context

Instructions или context, которые загружаются по умолчанию почти в каждой соответствующей сессии. Progressive Context Kit держит этот слой под явными budgets.

### Progressive loading

Подход, при котором работа начинается с минимально достаточного context, а дополнительные files, history, Skills и evidence подключаются только если они нужны текущей задаче.

### Phase

Ограниченный этап реализации с goal, tasks, acceptance criteria и ожиданиями по verification.

### Task

Единица работы внутри Phase. Для routine Tasks отдельные completion-report files не создаются.

### Acceptance criterion / acceptance gate

Условие, которое должно быть фактически подтверждено до завершения соответствующего Task или Phase. Незакрытая ручная verification всё ещё считается открытым gate.

### Completion Record

Компактный durable bridge, который остаётся в завершённой Phase. Он хранит только небольшой объём информации, нужный будущей работе при обычном progressive warm-up.

### Phase Completion Report

Подробный durable отчёт по одной завершённой Phase. В нём хранятся implementation notes, decisions, deviations, verification evidence и другая история, которая иначе раздувала бы hot context.

### `NEXT_SESSION`

Volatile hot navigation для следующего meaningful continuation. Этот файл перезаписывается, а не накапливается как история.

### `NEXT_SESSION_PROMPT`

Готовый continuation prompt внутри `NEXT_SESSION`. По правилу **Single-Focus Continuation** он содержит только один незакрытый execution target; будущие queued Tasks остаются в Phase/Roadmap, пока текущая цель реально не закрыта и evidence не сохранён.

### Handoff

Переход в конце сессии, когда агент сохраняет текущее state/evidence и готовит безопасное continuation для следующей сессии.

### Single-Focus Continuation

Правило: один handoff prompt содержит один незакрытый execution target. Если текущий Task, blocker или acceptance gate всё ещё открыт, prompt посвящён только его закрытию и не предзагружает следующий queued Task.

### Skill

Специализированный workflow, который подключается по типу задачи. Installed не означает loaded, а loaded не означает invoked для каждой задачи.

## Связанные гайды

- [`GETTING_STARTED.ru.md`](GETTING_STARTED.ru.md)
- [`HOW_PROGRESSIVE_CONTEXT_WORKS.ru.md`](HOW_PROGRESSIVE_CONTEXT_WORKS.ru.md)
- [`PROJECT_MEMORY_MODEL.ru.md`](PROJECT_MEMORY_MODEL.ru.md)
- [`UPDATING_RUNTIME.ru.md`](UPDATING_RUNTIME.ru.md)
- [`../visuals/README.md`](../visuals/README.md)
