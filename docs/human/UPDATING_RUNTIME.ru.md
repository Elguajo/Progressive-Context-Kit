# Безопасное обновление Project Runtime

> **Документация только для человека.** Она живёт только во Framework Source и не попадает в Project Runtime.
>
> English: [`UPDATING_RUNTIME.md`](UPDATING_RUNTIME.md)

Обновление Project Runtime должно сохранять project-owned state и заменять только framework-owned runtime material.

Схема границы: [`../visuals/framework-update-safety.md`](../visuals/framework-update-safety.md)

## Главное правило

```text
framework-owned → можно обновлять
project-owned   → нужно сохранять
```

К project-owned state относятся, среди прочего:

- `.progressive/project/` — долговременное состояние проекта;
- `.progressive/phases/`;
- `.progressive/completions/`;
- `.progressive/decisions/`;
- project-specific части инструкций, которые installer сохраняет;
- application/source files.

Не обновляй важный проект простым распаковыванием нового Runtime ZIP поверх существующей директории в надежде, что file collisions окажутся безопасными.

## Предпочтительный путь обновления

Из доверенного Framework Source checkout используй installer/update-механику:

```bash
python3 tools/init_project.py /path/to/project --update-framework --dry-run
python3 tools/init_project.py /path/to/project --update-framework
```

Для важного проекта или заметного framework update сначала запускай `--dry-run`.

## Совместимость старых инструкций

Installer распознаёт старые стандартные Personal/Standalone профили по точным отпечаткам
в `tools/legacy_agent_profiles.json`. Каталог поставляется с Framework Source; Git и сеть
для распознавания не нужны. Пользовательский текст после подтверждённого стандартного
профиля сохраняется под разделителем `PROJECT-SPECIFIC-INSTRUCTIONS`.

Новые установки и сгенерированный Runtime сразу содержат этот разделитель. Для добавления
локальных инструкций используй часть файла после него; правки внутри framework-owned
части без разделителя требуют ручного reconciliation и не перезаписываются автоматически.
Обновление проверяет совместимость и AGENTS.md, и CLAUDE.md до записи файлов.
`--dry-run` выполняет ту же проверку и возвращает ошибку для неизвестного формата.

Каталог — source-only compatibility evidence, а не дополнительный контекст агента. При
добавлении совместимости сохраняй точный отпечаток runtime-rendered стандартного префикса
(универсальные переводы строк, `rstrip()`), длину в символах и исходный commit. Не добавляй
пользовательские варианты и не распознавай инструкции только по заголовку/номеру версии.

## Что проверить после обновления

Запусти:

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

Затем проверь:

- текущее состояние проекта по-прежнему соответствует реальности;
- phases, completion reports, decisions и source files сохранены;
- root agent instructions сохранили project-specific suffix, если он был;
- normal context остаётся ограниченным;
- подробные completion reports остаются on-demand и не попали в warm-up.

## Когда нужно остановиться

Если update обнаружил collision в project-owned state, неизвестный формат root instruction file или другую неоднозначность, которая может разрушить intent проекта, не форсируй overwrite.

Безопасный update должен уметь точно показать, какие framework-owned файлы изменились, и подтвердить, что project-owned state остался нетронутым.
