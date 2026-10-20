# Lamentum (TrimUI Smart Pro S): roadmap для стабильных 30 FPS

**Аудит:** 2026-10-20, HEAD 4547117fb7b727bd7b8e12c68a2e3899a872c037, build202.  
**Назначение:** технический, исполнимый план экспериментов, НЕ обещание достигнутого FPS.  
**Статус игры:** настоящие main menu / slots / Options и управляемый UI доказаны. **New game, gameplay, звук, save/reload НЕ подтверждены.** Поэтому сначала функциональная проверка, затем игровые FPS.  
**Стек:** Nintendo Switch Lamentum, Unity 2019.4.4f1 IL2CPP/ARM64; guest Horizon + NVN translation через EGL/GLES на Mali-G57 в TrimUI Smart Pro S / SpruceOS; экран 1280×720, примерно 1 GiB физической RAM. Без Box64, без модификаций оригинального game image в репозитории. Все изменения к 435-file baseline только через runtime/lamentum-adapter.patch.

История и контракты: [README](../README.md), [architecture](architecture.md), [UI cbuf binding](ui-cbuf-binding.md), [catalogue tail](catalogue-tail.md), [loading memory](loading-memory.md), [porting log](porting-log.md). Исторические записи не являются текущими performance measurements.

## 0. Аудит существующего кода и чисел

**Главное свидетельство:** [build202 log](../evidence/ui-cbuf-fixed-01/latest.log) + [effective env](../evidence/ui-cbuf-fixed-01/env.json). Установленный ELF SHA256 ff4454232247b935748db7a76b05a7af27e62f2a189d199b49d7d6d93f9d1fd2. Длительность до TIME_LIMIT 520 секунд, последний представленный кадр 709. Из журнала рассчитаны распределения **708 строк T2P_SLOW_FRAME**. Это диагностический прогон, не quiet gameplay benchmark.

| Записанный показатель | P50 | P95 | Примечание |
|---|---:|---:|---|
| period-ms, вся серия | 620.0 ms | 1242.0 ms | медианный интервал ~1.61 кадра/с, не игровая оценка |
| replay-ms | 235.7 ms | 605.7 ms | только replay, не весь кадр |
| finish-ms | 0.1 ms | 0.6 ms | НЕ все потенциальные GPU waits |
| present-ms | 3.2 ms | 6.7 ms | presenter |
| swap-ms | 0.2 ms | 0.7 ms | внутри instrumented swap |
| readback-ms | 2.5 ms | 4.7 ms | diagnostic GPU readback |
| period-ms, frames 500–709 | 512.5 ms | ~676 ms | поздний прогретый участок |
| replay-ms, frames 500–709 | 96.9 ms | ~356 ms | поздний участок |

**Отдельно:** помодельная медиана (period - replay - present - swap - readback) для frame>=500 равна ~403 ms. Это пока **неатрибутированное время**, НЕ доказательство сна, низкой частоты или memory compression; в расчёте учитываются только названные поля. Медианы разных столбцов НЕ складываются. Цель 30 FPS требует full frame period <=33.33ms и correctness. Поздний diagnostic period ~513ms и replay ~97ms — разрыв очень большой, но возможный diagnostic overhead пока не вычтен.

**Почему эти данные нельзя принимать за финальный FPS:** env включал LC2_CBUF_AUDIT=64, COTM_CBUF_GL=32, LC2_PAIR_CENSUS=60, LC2_HID_WATCH=1, LC2_MENU_TRACE=1, MOMO_DIAG_MASK=1, MOMO_FBO_DIAGNOSE=1, MOMO_FBO_FRAME=300. Имеются GL readbacks, shader/UI receipts, trace и большой лог.

**Наблюдения с прямым адресом в коде:**

1. В build202 на завершении T2_GZRAM periodic: compressions=336501, faults=274244, restores=312330, scans=914, compressed=377.7 MiB, stored=82.5 MiB, reported saved=295.1 MiB. MemAvailable около 119 MiB, процесс VmRSS около 644060 KiB и VmSwap около 218912 KiB. Счётчики НЕ показывают CPU-времени компрессии; но это явный кандидат для instrumented A/B. Отключение механизма без дополнительного headroom рискованно.
2. В runtime/lamentum-adapter.patch, hunk **native/nvn_render.h**, ветка kind=7 для cbuf создаёт staging float array, копирует guest bytes и вызывает **glTexImage2D(GL_RGBA32F) для каждого активного uniform block/draw**, даже если содержимое и размеры не изменились. Это конкретный кандидат для reuse / glTexSubImage2D / identical-content skip, после замера.
3. NVN_DRAW_PROGRAM_PROFILE after-frame=660 за окно 60 frames перечисляет **1620 draw records** (~27 на кадр в профилированном наборе). Pair 12/14: 540 draws в target 1920×1080; pair 17/4: 600 draws через десятиуровневую bloom/downsample цепь 640×360 до 1×1. Это subset, не вся стоимость GL/Unity. Target 1920×1080 имеет 2.25× пикселей относительно физического 720p.
4. NVN_COMMANDS_EXECUTED показывает completed-with-glFinish=1; малый present finish-ms не исключает другие waits внутри queue. Уже была ошибка NVN_COMMAND_REUSE_BEFORE_COMPLETION при небезопасной схеме, а корректный SDL/KMSDRM surface lifetime измерен в build152.
5. Текущий port/Lamentum.sh по умолчанию: AW_RELEASE=1, LC2_GLES3=1, COTM_ASYNC_QUEUE=0, T2_GPU_PIPELINE=0, COTM_FB_PRESENT=0, COTM_GL_ERROR_IGNORE=0, LC2_TEXTURE_PAGEOUT=0 и memory floor **96 MiB**. Рабочий menu run применял diagnostic floor **32 MiB**, lossless file backing и GZRAM. Не считать diagnostic envelope полноценным production default.
6. Shader catalogue содержит 38 real translated/captured programs + 7 TEST substitutes. Исправление c4 -> NVN UBO1 в build202 — единичное и принципиальное. Регенерация всего каталога без точного сохранения provenance способна вернуть старую ошибку; для new shader tail пользоваться append-only tools/append_program.py.
7. Актуальный путь корректной графики включает sampler handles, cbuf unit isolation, embedded shader literals, deferred BC and stripe decode. Не откатывать эти исправления под видом performance optimisation.

## 1. Жёсткие правила всех экспериментов

- **Два независимых gates:** (A) правильный игровой кадр/управление/звук/save; (B) его полное frame-time <=33.33ms. Frame counter и FPS без реального игрового изображения не проходят gate A.
- Менять ровно одну переменную, хранить baseline ELF SHA256, git commit, owner image hash и manifest-pinned source identity. Сравнивать одну сцену/сейв и одинаковое реальное состояние после прогрева; 3 повторных A/B пары для спорных результатов.
- Отдельные серии startup, title/menu, New game transition, stationary gameplay, moving gameplay, interactions, bloom/effects и save/load. Не сравнивать cold loading A с warmed menu B.
- В release measurements **отключить диагностику**; diagnostic builds и glReadPixels могут менять profile. Логировать минимальными кольцевыми буферами вместо printf на каждый draw/SVC.
- Не обходить GL errors, zero shader contract, NVN command-buffer ownership, glFinish и fences с целью «ускорить». Не отключать CPU/memory safety governor и не снимать лимит 420 MiB GPU бюджетирования.
- Исходные NSO/RomFS/assets/ключи/сейвы/shader binary остаются только owner-local; публично в evidence — лог/stat/hash/свои исходники и проверенные captures.
- Проверять реальные DRM captures **при живом port PID**, а также cleanup (MainUI, CPU online mask, отсутствие зависших процессов). Перед опытами создать идентичный backup всех save files и прежнего ELF.
- На исходной плате ~1 GiB RAM, guest ZRAM и file backing занимают разные учётные домены; reported compression saving нельзя складывать с backing size как независимую освобождённую RAM.

## 2. P0-FUNC — прежде всего дойти до воспроизводимого gameplay

**Причина:** оптимизировать меню до 30 FPS бессмысленно, если последующий New game упрётся в новый shader, memory floor или сломанные спрайты.

**Пошагово:**

1. Зафиксировать билд202, identity SHA и его owner image. Проверить sha256sum -c tools/baseline-manifest.sha256 на отдельном baseline (435/435).
2. Через правильный Spruce principal flow открыть экран main menu, сделать screenshot реального KMS кадра, подобрать **New game**, затем Confirm. В build202 уже доказано открытие **Options**, не New game; не смешивать.
3. Запустить bounded longer run с локационным логированием guest shaders, service stops, загрузок и MemAvailable. Сохранять кадры после New game, реальные переходы между сценами, не JPEG «что-то нарисовано».
4. При ZERO_SHADER_NOT_PINN использовать строго code/control identity и tools/append_program.py. Не регенерировать runtime/lamentum-shaders-draft.h целиком. При новом pair записать stage, uniforms, sampler slot/offset, bank +3 mapping и correct cbuf binding. Провести host tests и сравнить UI text 202.
5. В gameplay отдельно собрать LC2_PAIR_CENSUS с коротким фиксированным окном и определить, задействованы ли 7 TEST substitutes. Они включают SSBO-skinning и MSAA/per-sample пути: не заменять их sampler2D без правильной семантики.
6. Проверить движение, взаимодействие с предметом, inventory, диалоги, stencil/alpha/lighting, смену сцены. При визуальных дефектах остановить FPS оптимизацию до точной shader/texture/state коррекции.
7. Проверить **слышимый** звук (AUDOUT nonzero недостаточно), сохранение -> quit -> cold start -> load -> совпадение позиции/инвентаря, затем полный возврат MainUI и восстановление CPU.
8. Повторить короткий smoke **без diagnostic draw/GL probes**; отдельно проверить, выдерживает ли launcher memory envelope. Не переводить 32 MiB floor в дефолт без safety acceptance.

**PASS:** правильный управляемый игровой кадр с воспроизводимыми состояниями/сохранением. **STOP:** любой shader stop, неверные pixels или конфликт сохранений. Никакой claim «играбельно» до gate.

## 3. P0-BENCH — чистый baseline + профиль diagnostic overhead

**Начальный controlled run** должен сохранять те же memory-параметры, на которых был получен build202 menu, но без дорогостоящей графической диагностики. Пример, запускать только после проверки idle MainUI и owner backup:

~~~sh
python3 tools/device_principal_test.py --budget 520 --wait 600 \
  --env LC2_GUEST_QUOTA_MIB=3072 \
  --env LC2_BC_LAZY_ALL=1 --env LC2_BC_LAZY_UPLOAD=1 \
  --env LC2_BC_FILE_BACKING=/mnt/SDCARD \
  --env LC2_BC_FILE_BACKING_EXTRA=/mnt/UDISK \
  --env LC2_BC_FILE_CAP_MIB=1280 \
  --env T2_MEMORY_FLOOR_MIB=32 \
  --env T2_GUEST_ZRAM=1 --env T2_GZRAM_BLOCK_KIB=16 \
  --env T2_GZRAM_COLD_MS=10 --env T2_GZRAM_TARGET_MIB=512 \
  --env T2_GZRAM_PERIOD_MS=20 --env T2_GZRAM_BUDGET_MIB=32 \
  --env AW_RELEASE=1 \
  --env LC2_CBUF_AUDIT=0 --env COTM_CBUF_GL=0 \
  --env LC2_PAIR_CENSUS=0 --env LC2_MENU_TRACE=0 \
  --env LC2_HID_WATCH=0 --env MOMO_DIAG_MASK=0 \
  --env MOMO_FBO_DIAGNOSE=0 --env COTM_GL_ERROR_IGNORE=0 \
  --evidence evidence/perf-quiet-b0
~~~

**Важно:** это только **диагностическая memory envelope**, не безопасный production preset; при memory floor/pressure быстро остановить, не пытаться вытеснить другие системные процессы. Не выставлять MOMO_FBO_FRAME и дополнительные dump flags. Проверить source getenv semantics: у некоторых переключателей даже строка 0 может отличаться от unset; если есть сомнения, запускать новый чистый shell с разрешённым env allowlist.

Порядок: historical diagnostic A -> quiet B -> quiet A/B повторения, при одном ELF, одинаковом menu/game phase. Записать реальное время достижения menu и начало последующего **steady** окна; сравнивать только одинаковые окна. Не выводить FPS из 709/520 (в этом интервале была и загрузка).

**Добавить инструменты (отдельный PR, не реализовано):**

- tools/lamentum_perf_observer.py: внешний process observer раз в 1–5s, /proc PID status/stat/io/schedstat, smaps_rollup (редко), task threads, MemAvailable, CmaFree, swap counters, thermal, cpu online/governor/freq; не опрашивать слишком часто.
- tools/analyze_perf.py: parser existing T2P_SLOW_FRAME with frames, period/replay/finish/present/swap/readback, median/P90/P95/P99/max и dropped/unknown spans, early vs late windows, gaps >100/250/1000ms; output JSON/CSV, input log and exact ELF SHA.
- Инструмент gated screenshot **только при live game PID**; sampling cadence не на каждый кадр, не считать запаздывающее возвращение MainUI доказательством правильного game capture.

**PASS:** три quiet-run профиля с цифрами P50/P95 и фиксацией diagnostic overhead; при сильном улучшении без probes пересмотреть весь следующий приоритет.

## 4. P1-TIMELINE — объяснить оставшиеся ~400 ms до любого render-tuning

**Проблема:** frame500–709 period p50=512.5ms, replay p50=96.9ms, остальные известные этапы единицы ms. Root cause находится **не обязательно в GPU**.

**Новый узкий LC2_FRAME_TIMELINE=1**, желательно preallocated ring + dump каждые 60/120 кадров:

1. CLOCK_MONOTONIC_RAW: previous present end, guest present-enter, command-buffer publish/snapshot, replay enter/exit, **каждый glFinish и eglMakeCurrent** на всех thread'ах, SDL swap enter/exit, owner presented frame generation.
2. CLOCK_THREAD_CPUTIME_ID и /proc/TID/schedstat для guest-main, render, input/audio, host compressor: разнести running, runnable-but-unscheduled, blocked-on-wait, page fault, GPU fence wait, sleep.
3. Guest SVC WaitSynchronization/SleepThread/WaitProcessWideKey/WaitForAddress и другие actual waits: count, requested duration, actual duration, guest caller PC. Особое внимание Unity PlayerLoop/frame pacing; не подменять guest deltaTime и не игнорировать sleeps без причинного теста.
4. CPU page-fault/major-fault и guest-memory restore events со thread ID и bins, но без полного trap printf. Для самого NVN replay делить wall и thread CPU, т.к. wall включает возможный scheduler wait.
5. Выводить per-frame mutually exclusive wall components с проверкой, что суммы объясняют >=95% period. Отдельно показывать overlap GPU vs CPU, не складывать inclusive durations.
6. После instrumented профиля выполнить **тот же ELF с instrument off**: overhead <5%, иначе sampling агрегировать ещё реже.

**Разветвление решения:** guest actual sleep -> выяснить timer/SDK contract; thread runnable but preempted -> CPU affinity/load; time on decompression -> §5; high guest CPU -> profiled SDK/IL2CPP hotspot; queue waits -> §8; high render CPU -> §6. Не начинать переписывать backend до attribution.

**PASS:** >=95% frame period атрибутировано по фазам с чистым B comparison. **STOP:** попытка уменьшить sleep без знания guest caller semantics.

## 5. P1-MEM — оптимизация частой guest-page compression/fault

**Исходная проблема:** 336501 компрессий и 274244 faults в build202. Имеется значительная заявленная экономия памяти, поэтому unsafe simple OFF не подходит.

**Точки:** native/t2_guest_memory.h, guest mmap/alias ownership, memory.h, native/nvn_textures.h, LC2_BC_FILE_BACKING и LC2_BC_LAZY_UPLOAD. Добавить счётчики compress_CPU_ns, restore_CPU_ns, faults per guest page, recompression within 10/50/200ms, pages pinned/excluded, effective saved MiB and fault stall ms; не смешивать со system swap.

**A/B-матрица (одна переменная за раз, с одинаковым ELF и контролем RAM):**

| Тест | Изменение от current diagnostic memory flags | Что проверяет |
|---|---|---|
| M0 | cold=10ms, period=20ms, budget=32MiB, block=16KiB | тихий контроль |
| M1 | T2_GZRAM_COLD_MS=50 | повторно сжимались ли горячие страницы |
| M2 | T2_GZRAM_COLD_MS=100, затем 200 | CPU savings против RAM residency |
| M3 | T2_GZRAM_BUDGET_MIB=16, отдельно 8 | уменьшение конфликтов с guest CPU |
| M4 | T2_GZRAM_PERIOD_MS=50, отдельно 100 | частота сканирования и pressure |
| M5 | selective no-compress hot ranges, **только** exact owner accounting | исключить систематический fault churn |
| M6 | T2_GUEST_ZRAM=0, **только** при доказанном headroom | проверить upper bound эффекта компрессии |

Для M1–M4 проверять корректную семантику cold/period/budget в baseline до запуска; снимать P50/P95 period, replay, host compression CPU ns, page faults, VmRSS/VmSwap/PSS, minimum MemAvailable/CmaFree, kernel OOM/kill, load completeness. Не менять одновременно file backing quota/texture cap. При floor=32 и MemAvailable ~119 MiB нельзя предполагать, что компрессия отключается без вреда.

**M5:** сначала точная read/write и lifetime карта адресов (mutable Unity heap, repeated hot pages, NVN GPU pools, audio/shared IPC). Только доказанные safe to exclude страницы, без произвольного madvise или pageout. **PASS:** repeatable whole-frame P95/guest CPU gain, no loss of texture/saves, safe memory. **STOP:** floor/OOM, alias invalidation, swap storm, regressions.

## 6. P1-CBUF — GL_RGBA32F uniform-texture uploads per draw

**Подтверждено в overlay:** native/nvn_render.h, branch u->kind==7, memcpy staged guest range, glActiveTexture, glBindTexture, glTexParameteri, glTexImage2D, glUniform1i. Здесь потенциально много повторений с 144–368-byte active cbuf data; текущее распределение повторов и стоимость пока **не измерены**.

**Подробные шаги:**

1. Добавить counters: kind7 count/frame, bytes copied, unique active cbuf snapshots, unchanged bytes count, GL texture allocations and redefinitions, CPU nano per step. Разнести pair12/14 UI от pair17/4 bloom и всех gameplay pairs.
2. **C1:** хранить texture generation, GL unit assignment, allocated format/width/height и active program/context. glTexImage2D использовать при первом allocation/resize; при same-size changed data — glTexSubImage2D. Не считать флаг gl object name достаточным: EGL context loss/recreate и allocator reuse инвалидируют состояние.
3. **C2:** upload skip только после exact byte comparison и matching generation; дешёвый 32/64-bit hash может служить предфильтром, не доказательством равенства. Сравнивать именно **actual size and padded bytes**, не всю 65536-byte max cbuf каждый draw.
4. **C3:** skip повторных glUniform1i/glTexParameteri/glActiveTexture only when tracked GL state confirmed unchanged. При program switch, other textures, audio/EGL context and distinct stage bank — invalidate appropriately.
5. **C4:** GL buffer/PBO/immutable storage и ring для GPU in-flight read — только если профилирование доказывает выгоду. Нельзя менять текстуру, которую GPU читает из предыдущей queue generation, без правильного fence/serial и lifetime.
6. Текущая unit isolation после build177 и bank4->UBO1 после build202 обязаны остаться. Host tests tools/test_cbuf_units.c, tools/test_ui_cbuf_binding.py, tools/analyze_ui_cbuf.py, сохранение shader-catalogue exact identity; сравнить KMS UI text/selected item, alpha, UV и scene texture.
7. Не делать fallback to any nonempty cbuf глобально: binding должен быть выведен из compiler instance name и SDK hardware bank = NVN slot +3, а не из ordinal/bare block type.

**PASS:** уменьшение upload-time and entire replay p95 на одном кадре при идентичном GL output / game state. **STOP:** cbuf collisions, пропажа UI, bad transform или unknown resource lifetime.
