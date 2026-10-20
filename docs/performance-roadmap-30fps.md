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


## 7. P1-REPLAY — где именно тратятся 97–236 ms replay

**Место внедрения:** базовые native/nvn_replay.h, native/nvn_render.h, native/nvn_samplers.h, native/nvn_shaders.h, native/nvn_textures.h, native/nvn_framebuffers.h, native/nvn_commands.h, native/nvn_queue.h; изменения — только в runtime/lamentum-adapter.patch. Реальная измеренная цена каждой функции **не известна**. Пример WoL-методики: [roadmap-roundup](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/evidence/roadmap-roundup-20261016/README.md): в **другой** игре разбили replay на first texture resolve, state changes, memory transfers и shader cost. Переносить можно **метод**, а не ms или конкретный patch.

### 7.1. Сначала low-overhead profile

Добавить LC2_REPLAY_PHASES=1 с per-frame/per-program/per-operation агрегированием, без подробного stdout на каждый GL call. Для каждого command-list и serial зафиксировать следующие exclusive CPU ns и counts:

- queue snapshot/record parsing / guest->host command copy, command count и bytes;
- draw dispatch до GL: sampling handle decoding / descriptor lookup / texture lifetime; отдельно first-resolve и повторный resolve идентичного ключа;
- zero_texture_refresh: время BC decode, memory copy, glTexImage/Upload, dirty flags, bytes, allocation and GPU budget;
- shader lookup (catalogue hash), compile/link и shader switch; program bind, uniform location lookup;
- cbuf GPU upload (см. §6), sampler state, texture bindings, framebuffer attachment/lookup/rebind, depth+stencil, blend, scissor, viewport;
- vertex/index: extract guest range, format conversion, malloc/realloc/copy, glBufferData/glBufferSubData, draw GL API call overhead;
- non-draw records: TextureWriteTexels, clears, render target switches, barriers, buffer copies, command reuse, resource creation/deletion;
- **все** glFinish/GLsync/eglMakeCurrent, время scheduler wait/CPU thread time отдельно от GL completion.
  
В конце окна печатать примерно: frame range, total replay CPU wall, host thread CPU, non-draw / draw, per-op count, bytes and inclusive/exclusive durations; диагностический журнал допускает одну строку каждые 60 кадров плюс on-exit. Подтвердить missing bucket <=5% в пределах replay. Гистограмму не усреднять только по удачным frames: включить P95 и rare >100ms. Фаза shader first-use должна быть отдельной от steady-state.

### 7.2. Кандидат A: быстрый повторный sampler/texture resolve

Если значительны одинаковые handle resolve, внедрить **bounded** per-context cache с ключом: texture pool ID/generation, descriptor index, sampler ID/generation, view format, mip, layer, swizzle, target type, backing modification generation. Cache hit допускается только при сохранённом guest descriptor и GL texture lifetime. На TextureWriteTexels, texture pool unregister/re-register, free, recreate, framebuffer aliasing и context loss — invalidation. В частности нельзя reuse old texture после write в тот же memory pool по одному совпадению handle.

Проверить на первом/втором resolve одного handle, затем на полном кадре. Output: hit/miss, invalidations, correctness, CPU p50/p95, GL allocations. В WoL first per-frame resolve оказался дорогим, но **нет доказательства** такой же причины в Lamentum. Не внедрять cache вслепую.

### 7.3. Кандидат B: GL state shadowing

Добавить точную per-EGL-context shadow state таблицу для текущих shader/program, active texture unit, GL texture bindings на каждом unit/target, GL FBO, GL array/element buffers, blend/scissor/depth/stencil, viewport. Перед вызовом проверять identity+generation, но **действительное состояние** между guest shader passes может меняться в native present, diagnostic draw и FBO helpers. Каждый неучтённый внешний GL entry должен инвалидировать соответствующую часть кэша, иначе будет графическая регрессия.

Сначала только telemetry «would_skip_calls» без изменения поведения; затем оптимизировать **один** вызов/семейство. Сравнивать GLenum errors, real KMS captures, guest state parity и whole-frame latency. glGetIntegerv/glCheckFramebufferStatus нужны для bounded diagnostic, но не должны стать частью нового hot path.

### 7.4. Кандидат C: buffers и per-draw allocations

Собрать live counts realloc/malloc/free, glBufferData vs glBufferSubData, amount of vertex/index copying и сколько раз identical guest byte range преобразуется повторно. Если churn действительно велик — persistent VBO/IBO ring / preallocated scratch и cache conversions с identity, source write epoch и proper GL in-flight fence. Для динамического UI/stencil/particle geometry не считать одинаковый адрес guest memory неизменными данными. Мерить RAM delta: оптимизация CPU не должна удвоить resident memory и спровоцировать ZRAM faults.

### 7.5. Кандидат D: framebuffer/pipeline transitions

Проверить per-frame FBO cache hits/misses/rebinds, RT attachment validity, render-pass boundaries, repeated glCheckFramebufferStatus and glGetError; отделить **diagnostic** проверки от обязательной validation. Tile-based Mali может выигрывать от уменьшения render-target switches и лишних stores, но любой glInvalidateFramebuffer допустим только после последнего чтения attachment; иначе разрушится bloom/UI/final composite. Включить preserve/restore текущего FBO после readback diagnostic.

### 7.6. Batching и ограничения

Объединять draw commands можно лишь при **доказанном** совпадении target, ordering, texture/UBO, blend, viewport/scissor, alpha, depth/stencil, fragment side effects и no memory barrier. Пара 12/14 может рисовать 9 отдельных UI объектов на кадр — нельзя объединять просто по имени program. Сначала census потенциально совместимых consecutive draws с сохранением guest order и per-frame visual diff; далее experimental batch в opt-in branch.

**PASS:** уменьшение **общего** period P95 (а не только replay CPU, который может перейти в GPU finish); KMS/GL parity, no resource-generation races, одинаковые saves. **STOP:** новая строка STOP, wrong stencil/UI, shader remap или неизвестное владение объектами.

## 8. P1-720 — определить владельца внутреннего 1920×1080 и тестировать 720p

**Факт:** на физическом 1280×720 panel встречаются NVN draw targets **1920×1080** (например UI 12/14 и pair 11/9). В 1920×1080 ~2.25 раза больше pixels, чем в 1280×720. Потенциальное сокращение raster/workload ≠ автоматически 2.25× FPS. При диагностических 400 ms вне replay внутреннее разрешение может быть второстепенным.

### 8.1. Найти источник размера, а не угадать

1. В low-overhead trace выделить resource IDs для всех 1920×1080 RT, initial NVN TextureBuilder, memory pool owner, target flags/format/MSAA, attach/reuse/readback, number of draws/frames, framebuffer and sampler consumers; отдельно отметить конечный 1280×720 screen и postprocess.
2. Read-only анализ оригинальных IL2CPP metadata + main NSO в owner workspace: поиск сериализованных component fields/MonoBehaviour и native call-sites (Unity Screen.SetResolution, RenderTexture.GetTemporary, new RenderTexture, CanvasScaler, player graphics settings). Это **список для поиска**, не утверждение, что названные API вызываются этой игрой.
3. Сопоставить события и значения **1920, 1080**, возможные reference resolution / render scale / dynamic resolution, последние изменения UI projection. Изучить Options (в build202 экран виден) на реальные настройки resolution/effects. Не считать handheld/TV request источником внутренних размеров без trace.
4. Сформировать original->candidate матрицу: размер RT, viewport/scissor, matrices/UBO, sample UV, text/UI point size, input hitboxes, LOD and postprocess dependency. При mode change запрашивать полную reallocation resource family, не изменять размер объекта под старой descriptor identity.
5. Если найден **owner-specific** компонент, внедрить *guarded* optional override его значения на 1280×720/scale 2/3 только для Lamentum с точным main NSO/metadata SHA. Изменять owner file в публичном репозитории нельзя; adapter должен либо корректно и проверяемо менять временную копию state, либо описать owner-local patch workflow.
6. Если owner component не найден, рассмотреть backend virtual resolution translator (logical 1920x1080 -> physical 1280x720) только с полным преобразованием FBO sizes, render/copy subrectangles, texel offsets, shader sampling LOD, viewport/scissor, clipping, UI pixel snapping, pointer coordinates и all render-target consumers. **Это дорогой/high-risk вариант**, не первая попытка.
7. А/B: original 1080 -> 720, затем отдельный 960×540/640×360 quality preset только при приемлемом UI. Желательно оставить UI native-res, менять лишь scene/lighting intermediates и применять upscaler после verify.
8. Проверить actual KMS frames из title, main menu, Options, inventory, moving scene, bloom/highlights, text readability, clip/stencil; сравнить actual GPU memory and GPU query time, CPU replay, P95 period, startup memory.
9. При повторной сборке shader catalogue **не** возвращать build201 c4 binding0. Учитывать уже выведенную projection UI ~2/1920,2/1080 в 160-byte UBO1: простое resize RT при неизменённой matrix может скрыть текст.

**Сравнение с WoL:** там конкретный owner Unity UpRender (которого существование в Lamentum НЕ установлено) позволил улучшить measured FPS от ~24 до ~33–34 в одной сцене. Нельзя переносить field offsets, title hashes и выводы о docked mode из [WoL roadmap](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/docs/optimization-roadmap.md). Измерить источник **самой Lamentum**.

**PASS:** owner-visible pixel/interaction correct, repeatable whole-frame gain при одинаковой scene+clocks и memory safety. **STOP:** смазанный текст, screen/input misalignment, неправильная альфа или unresolved resource alias.

## 9. P1-POST — bloom/noise/post-processing на Mali

**Точки:** NVN pair17/4 -> 10-level downsample targets, 11/9 composite/near-composite и final present; нужны actual pass dependencies. Опциональная UI настройка Noise effect уже доступна; **не утверждать**, что она отключает bloom.

**Методы в порядке цены/риска:**

1. Создать граф per-pass: input texture IDs, output RT/format/size, draw count, shader pair, clear/load/store, following users, aspect ratio; пометить lifetime каждого промежуточного attachment.
2. Измерить cost каждого pass CPU и GPU, если Mali/EGL поддерживает EXT_disjoint_timer_query (иначе report not available). GPU timestamp профилировать редко и проверять disjoint; glFinish после каждого pass исказит результат.
3. Сначала встроенная настройка Noise effect On/Off и, если существует, brightness/shadow/effects presets — одна настройка на run, same scene; оценить actual frame delta и KMS quality. Изменение noise ≠ автоматическое отключение blur/lighting.
4. Если дорог **именно** bloom: quality tier через строго установленные guest shader uniforms/source-provenance, уменьшить число уровней downsample (напр., 10->6 только когда final consumers перестают ссылаться на хвост), sample taps/radius или resolution **без изменения оригинального mode**. Следить за alpha, color space/sRGB, temporal effects.
5. Если дорог FBO change: grouping безопасных последовательных pass, reuse FBO objects, remove redundant state binds. Mali tile discard/invalidate только после последнего reader; no blind glInvalidateFramebuffer. Не вводить искусственное выключение glBlend/glDepth/glStencil.
6. Компонентные тесты shader: exact code+control hash; mat/UV/texelFetch coordinates, shader literal bank и sampler metadata остаются pinned. Снять изображения для темных/светлых сцен и меню, а не только pixel count.
7. Продвинуть quality option Original/Performance **только если** эффект на реальном игровом профиле заметен и качество согласовано; по умолчанию оставить original until accepted.

**PASS:** корректный performance preset с измеренной экономией GPU/frame-time и обратимостью. **STOP:** едва видимый интерфейс или эффект иного цвета/сломан bloom, выигрыш <= noise.

## 10. P2-GPU-MEM — оптимизация BC atlas, GPU residency и загрузки

**Подтверждённые существующие решения, которые не надо заново «изобретать»:** BC3 atlas 8192×4096, 128-row stripes вместо полного 128 MiB RGBA transient, deferred BC upload, lossless file backing после полного write, bounded GPU texture budget **420 MiB**, earlier load floor experiments (см. [loading-memory](loading-memory.md), [loading-memory-170-174](loading-memory-170-174.md)). Компрессор guest pages и file-backed bytes нельзя просто складывать.

1. Новая telemetry таблица resource ID -> guest pool alias and write epoch -> decoded/resident GL texture and format/mips -> actual last use/first use, create/destroy timestamps. Считать unique guest backing ranges по **union**, не по сумме virtual spans; GPU committed bytes не приравнивать к process RSS/PSS.
2. Профилировать именно повторную zero_texture_refresh / LC2_BC_MATERIALIZED и TextureWriteTexels: allocation, BC3 decompression, GPU upload, driver CPU time, stalls, pages read from backing. При повторной materialization искать invalidation loop / dirty range. Exact write-range epochs плюс generation IDs для проверки skip reupload.
3. Оптимизировать полноразмерные uploads только при строгом immutable-content proof. Если атлас часто меняется, partial dirty region upload через glTexSubImage2D вместо полного, с проверкой BC tiled decode, aligned compression blocks, surface pitch/stride, mip and swizzle.
4. Проверить natively supported compressed texture formats **на устройстве**: GLES extensions и независимый pbuffer upload/readback. Возможность ASTC на другом порте West of Loathing не гарантирует BC3->ASTC поддержку/качество и библиотеку на Lamentum.
5. Если supported, owner-local **content-addressed** ASTC side-cache для небольшого allowlist неизменных atlases: source SHA, exact dimensions/mip/format/color space, deterministic encoding quality, correct alpha, room on SD, fallback to existing lossless BC path. Не публиковать proprietary texture/payload; при mismatch never cache hit. ASTC может быть **lossy**, это отдельный quality gate.
6. Для inactive textures: не делать eviction/decommit guest bytes из pagemap zeros или таймера. Требуется реально доказанный owner lifetime + reconstruction path + no in-flight framebuffer/sampler readers, новый generation and fence. 420 MiB GPU cap не отключать.
7. I/O traces: SD/UDISK fileback cap/latency, statvfs disk free reserve, blocked pread, page faults, deferred upload. Стратегия background prefetch допустима только если guest dependency/barrier и RAM safety установлены.
8. Сравнить menu->New game transition, one interior and combat/effects phase, not raw count textures initialized; memory floor=32MiB не становится автоматически default.

**PASS:** меньший P95 stalls/real GPU residency при корректной scene/texture colour и сохранённом headroom. **STOP:** memory floor, corrupted texture, aliases, long disk stalls, GPU OOM. Не заставлять устройство swapoff.

## 11. P2-SYNC — NVN queue / GPU pipeline без небезопасного early completion

**Исходно:** COTM_ASYNC_QUEUE=0 и T2_GPU_PIPELINE=0 — измеренный стабильный синхронный путь. Ранее был NVN_COMMAND_REUSE_BEFORE_COMPLETION; SDL/KMSDRM recreates EGL surface after first fullscreen swap, что уже обрабатывается [loading-memory](loading-memory.md). COTM_FB_PRESENT=0, strict GL errors; без новой работы не переключать на framebuffer-copy путь.

1. После §4/§7 получить **все** GPU waits, resource producer/consumer and command serial; выяснить, есть ли >значимый CPU idle, когда GPU занят, и достаточно ли резерва RAM на async queue.
2. Для каждой command list: generation, writer publication, reader replay start/end, resources touched, GPU submission completion, first allowed recycle. Составить serial ownership contract; тест на повторное использование арен до fence, stale pointer, context loss и wraparound.
3. GLsync/fences: проверка GLES3/extension support, insert fence **после** producer commands, glFlush as needed, explicit client wait/complete event, never mark completed simply because producer thread dispatched. Fence object lifetime and GL context ownership должны быть проверены.
4. Сначала separate opt-in experiments COTM_ASYNC_QUEUE=1 vs 0, затем T2_GPU_PIPELINE=1 vs 0, а потом 1/1 при прошедших independent tests. Для каждого variant backed-up binary and known-good revert, test idle/UI/moving and scene transition.
5. Track output full-frame and P95, not short local replay ns; если stalls переедут в glFinish или возникнут lost/black frames, это не улучшение.
6. GL state per context must be explicitly invalidated on surface recreate, render/present context handoff, shader resource recycle; не игнорировать EGL_BAD_SURFACE, не подменять GPU completion timestamp CPU time.
7. Если стоимость sync мала, оставить верный synchronous path и закрыть пункт OFF: не тратить время на параллелизм ради потенциальных +0–1ms.

**Hard STOP:** NVN_COMMAND_REUSE_BEFORE_COMPLETION, NVN_QUEUE_CONTEXT, NVN_PRESENT_CONTEXT, EGL_BAD_SURFACE, black/tearing, stale uniforms or command memory reuse.

## 12. P2-CPU — scheduling/affinity, Unity и compiler flags

**Реальные наблюдения:** HOST_CPU_AFFINITY guest-main cpus=0; runtime launcher временно включает CPU0–3 и восстанавливает их на EXIT. Нельзя предполагать «core0 медленный» без системных данных. Spruce/OS может иметь свою раскладку CPU, thermals and governor.

1. Снять /sys/devices/system/cpu/{online,cpufreq/*}, доступные per-core freq, topology, /proc/TID schedstat, thermal and throttling while running. Сравнить guest CPU thread time vs runnable delay and zram CPU. Сбор извне, не forced clocks.
2. One-factor A/B affinity: pinned0 vs exact allowed healthy core(s) vs scheduler; **не** менять Horizon guest semantics и приоритеты без trace потока. Сохранять initial online mask и восстанавливать в любых exits/errors; CPU reallocation не должна повреждать input/audio threads.
3. Sampling native guest PC/callgraph с read-only symbol/IL2CPP lookup (hash-pinned owner image) — only if large guest CPU time. Узкие SVC stubs/TLS/IPC locks/memcpy/allocator paths оптимизировать с ABI parity, property tests и no title patch.
4. Compiler: проверить actual native/build.sh команду baseline и wrapper tools/cc-lamentum.sh (сейчас вызывает GCC with inherited flags, -DZERO_ZX_GAME=0). После baseline смотреть -O2 vs -O3, LTO, PGO только при отсутствии correctness issues, full source-parity and owner-local representative profile. Сравнить cold compile, binary size, RSS, compile errors, debug metadata, safety checks.
5. Texture/shader interpretation in guest может быть горячим: hash lookup/format conversions/GLSL compile, только если §7 показывает регулярную нагрузку. При уже pinned static shader literal specialization нет смысла заново делать эту оптимизацию.
6. Не рекомендовать постоянное изменение CPU governor, разгон, undervolting, min_free_kbytes, swappiness и zram swapoff: hardware, battery/heat, safety и результаты предыдущих неудачных memory probes — отдельные факторы.

**PASS:** повторяемые выигрыши full-frame P95 в реальном gameplay, no temperature/sound/input regressions and restored Spruce CPU mask.

## 13. P3 — другие варианты, которые нельзя делать вслепую

| Предложение | Приоритет/вердикт | Условие, которое оправдывает тест |
|---|---|---|
| Просто снизить physical SDL/KMS mode до 720 | Уже panel 720; это **не** Unity 1080 target | доказан owner internal scaling |
| Force Handheld вместо Docked / fake VI resolution | Не делать по аналогии с WoL: SDK/Unity разные | наблюдён call и verified consumer |
| glFinish bypass, fake command completion | ЗАПРЕЩЕНО для release, ранее был resource reuse stop | serial+fence ownership доказаны |
| Always enable async | Не default | significant sync waits + stage-level safety |
| Disable all ZRAM/fileback | Риск memory floor/OOM | продемонстрирован точный resident RAM headroom |
| T2_MEMORY_FLOOR_MIB=0 или снять GPU 420MiB cap | Нельзя использовать как FPS toggle | новая безопасная accounting model |
| Global sysctl/swapoff/forced clocks | Не предлагает performance fix | отдельная reproducible hardware cause |
| Remove bloom/UI/particle draws | Некорректный rendering | explicit reversible visual quality mode |
| Подменить shader TEST program нулевым цветом | Не годится для gameplay | shader semantically verified or guarded unused |
| Сгруппировать все draws одинакового shader | Опасно для alpha/depth/UI order | exact dependency and state equivalence |
| Rewrite runtime to Vulkan / direct DRM zero-copy | Долгосрочный R&D: огромный portability cost | доказан принципиальный GLES bottleneck |
| Native Unity ARM64 game build | Не доступен без source/engine-specific port | owner has rebuildable game source |
| Увеличить логирование для поиска FPS | Дополнительный overhead | bounded trace and quiet comparison |
| Играть через Box64 | Не подходит задачам native ARM64/Horizon, исключено | не рассматривать |
| Отключать kernel safeguards или patch proprietary image | Не требуется | никогда как незащищённый performance workaround |

## 14. Приоритетный execution plan с проверками и результатами

| Этап | ID | Чёткое действие | Выходной артефакт | Решение |
|---|---|---|---|---|
| P0 | F0 | New game -> управляемая сцена, звук, cold save/load | visual+state screenshots, exact binary, logs | нужен до FPS claims |
| P0 | B0 | Diagnostic vs quiet one-variable A/B | period/replay p50/p95, observer | пересчитать приоритеты |
| P0 | T0 | Timeline wall vs CPU vs wait, >95% attribution | CPU/gl queue/thread spans | устранить крупную задержку |
| P1 | M0–M5 | Guest compression cold/budget/fault A/B | safe headroom, fault stalls, frame P95 | оставить лучший или закрыть |
| P1 | C1–C3 | cbuf TexImage->guarded subimage/reuse | GL op count, CPU, pixel parity | только с cache generation |
| P1 | R1–R4 | samplers/GL state/VBO/FBO hotspot | replay stage timeline and paired A/B | только по фактической цене |
| P1 | G1 | owner 1080 target -> scoped 720p | same-scene screenshots and memory/FPS | если proven consumer |
| P1 | G2 | postprocess/bloom opt-in preset | explicit image quality vs perf | если GPU hotspot |
| P2 | M6 | residency/BC decode/ASTC side cache | verified object lifetime/cache hash | если significant pressure |
| P2 | Q1 | fences/async only when eligible | serial ownership proof | default OFF until passed |
| P2 | C4 | affinity/CPU/compiler opt-ins | clocks/thermal, P95 | no regressions |
| P0-final | A0 | extended gameplay, save/load, clean package | release acceptance evidence | freeze release flags |

**Распределение time budget — не общая сумма из medians.** На заключительном профиле для **каждого** кадра вычислить guest CPU, render CPU, waits, GPU completion, present, а затем сравнить p50/p95 distribution. Если чистый B0 даёт резкое ускорение из-за отключения диагностики, следовать актуальному bottleneck, а не историческим приоритетам. Если воспроизводимый gap ~400ms сохранился — T0/M0 выше shader tuning. Если gameplay значительно тяжелее меню, составить его отдельный список проблем.

## 15. Формат evidence для каждого PR: обоснование, воспроизводимость, откат

Делать один маленький opt-in feature/PR за раз. PR description содержит exact code lines, скрин текущего симптома, контрфактическую гипотезу («если CBUF повторяется, bypass сэкономит X ms»), **измерение X до изменения**, safety constraints, тесты и критерий исключения гипотезы. Не выставлять feature default=1 до полного acceptance.

Рекомендуемая структура, без game binary и пользовательских saves:

~~~text
evidence/perf-<ID>-<unique-tag>/
  README.md               источник, версия, сцена, намерение A/B
  identity.json           repo commit, baseline manifest hash,
                          ELF SHA256, owner image/section SHA256,
                          shader catalogue SHA256, device/OS identifier
  env-a.json              флаги, clocks/governor, memory envelope, phase
  env-b.json              ровно один изменённый фактор
  frame-a.csv             present serial, monotonic_ns, phase and duration
  frame-b.csv             те же колонки, provenance и missing samples
  observer-a.csv          CPU/TID, faults, RSS, PSS/SwapPSS,
                          MemAvailable, CmaFree, temp, swap IO
  observer-b.csv          те же показатели
  summary.json            p50/p90/p95/p99, counts and false/missing frames,
                          differences, outside confidence/noise limits
  screen-a.png            снято через реальный DRM, при живом game PID
  screen-b.png            эквивалентная сцена, original screenshot preserved
  cleanup.json            Game PID=0, MainUI=1, principal restored,
                          CPU mask original, no leaked subprocesses
~~~

**Строгий процесс**: source+image pin -> verify build/test -> backup working binary & saves -> check idle device/disk reserve -> run A -> cleanup proof -> run B -> cleanup proof -> repeat matched pairs -> analyze distributions -> human review screenshots/input/audio/save -> decide default/rollback. Структура Git evidence не должна включать оцифрованные NSO fragments, RomFS, keys, user save data и необработанные original shader blobs.

**Цифры:** throughput=number_of_presented_frames / measured_steady_elapsed_seconds, median fps=1000/median_period только как отдельная статистика, **не** воспринимать как panel FPS без подтверждённой кадровой последовательности. Считать P95/P99 spikes и missed vsync; отбрасывать startup и scene transition только **в отдельный отчет**, не скрывать плохие лаги gameplay. Презентация в 60Hz может требовать равномерной выдачи одного игрового кадра за два scanouts; внутри 30 FPS кадр <=33.333ms (с учётом очереди и джиттера). Указать sample frame count, time window, phase, loading fraction and instrumentation overhead.

**Пререквизиты и host tests:** sha256sum -c tools/baseline-manifest.sha256, все доступные tools/test_*.py и C host fixtures из репозитория, UI cbuf replay test, launcher CPU restore test, shader append-only test, GL texture lifetime/invalidation tests. Полный AArch64 cross-build в pinned container и read-back SHA256 установленного ELF; при любых отказах использовать сохранённый предыдущий бинарник. Скрипт tools/device_principal_test.py сейчас не является универсальной лабораторией: он использует owner-specific SSH/device path и MainUI handoff; адаптацию нужно делать в контролируемом owner workspace и не запускать вслепую на чужом устройстве.

## 16. Definition of done и stop criteria

**Не объявлять 30 FPS достигнутыми, пока:**

1. Версия ELF и owner-generated image действительно достигает воспроизводимой настоящей игровой сцены, её можно контролировать физическим TSPS controller, правильный KMS 1280×720 вывод без пропадающего текста/пунктов меню, stencil, lighting, bloom, alpha и wrong cbuf.
2. Есть настоящие audible sound/SFX, inventory, диалог/interaction, save -> quit -> cold start -> load и подтверждённое сохранённое состояние, корректное завершение и MainUI/CPU restoration.
3. Имеется **не менее трёх** независимых warm-scene runs по 60 секунд каждое, в одинаковых состояниях и при измеренных clocks/thermal; отдельно stationary и moving routes, effects/interior и transitions. На gameplay **P50 <=33.33ms и P95 <=33.33ms** full frame; P99 <=50ms целевой дополнительный порог, без регулярных >100ms зависаний. Если строго P95 33.33 не достигается — статус «не достигнуто», даже при средних 30.
4. Для A/B зафиксированы latency breakdown, diagnostic overhead, real presented throughput и исключены визуально неверные/потерянные кадры. Нет необходимости искусственно ускорять guest clocks или игнорировать shader/resource errors.
5. MemAvailable/CmaFree, SwapPSS, system major faults, temperatures не демонстрируют опасный тренд; нет OOM, kernel crash, сломанных save files или остаточных процессов. Производственный memory floor/flags отдельно доказаны, а не скопированы из 32MiB diagnostics.
6. Source parity проверена (baseline identity, adapter patch, GLSL source catalogue, конкретный ELF); собранные evidence доступны, проигравшие варианты имеют честный OFF/rollback.

**Stop rules для отдельного performance feature:** FPS различия в пределах run-to-run noise (после 3 A/B), выигрыш replay полностью переехал в GPU wait, потеря ресурса/текста/UI, memory floor/OOM, нарушение CPU restore, неизвестная зависимость guest buffer, неверный shader program identity. Тогда **не** добавлять flag в release, сохранить evidence и закрыть гипотезу.

## 17. Внешние материалы и порядок следующей работы

- [West of Loathing optimisation-roadmap](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/docs/optimization-roadmap.md) и [2026-10-16 measured frame breakdown](https://github.com/ruslan-k/west-of-loathing-portmaster-tsps/blob/main/evidence/roadmap-roundup-20261016/README.md): проверенная методика измерений, feature flags и доказательства, что owner-level Unity 720p может помочь; *не* готовый port-specific patch Lamentum.
- [Arm Mali: framebuffer handling](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/mali-performance-2-how-to-correctly-handle-framebuffers): использовать load/store/invalidate лишь с просчитанной dependency и tile-based lifetime.
- [Mali tile-based rendering guide](https://documentation-service.arm.com/static/636dfb934e6cf12278ad8c27): внешняя документация, не устройство-специфический benchmark.
- Existing [UI cbuf binding](ui-cbuf-binding.md), [cbuf isolation](cbuf-unit-isolation.md), [shader literal bank](shader-literal-bank.md), [probe-disabled fragment](probe-disabled-fragment.md), [shader tail](catalogue-tail.md) и [loading 170–174](loading-memory-170-174.md) содержат применимые exact provenance и previous failure boundaries.

**Рекомендованный следующий эксперимент — не ещё один shader tweak:**
(1) подтвердить New game и игровую корректность F0; (2) получить clean performance B0, иначе цифры build202 нельзя интерпретировать; (3) измерить wall+CPU timeline T0, установить природу ~400ms; (4) если compression действительно платная — M0–M4, иначе сразу CBUF/replay c конкретным ms профилем; (5) после этого owner-specific 720p (если 1080 target окажется критичным). GPU bloom, ASTC, async и compiler — при фактическом профиле и с жесткими gates.

**Примечание о выполнении:** весь этот roadmap создан по source/evidence аудиту GitHub; новых handheld запусков, 30 FPS замеров, patch игрового ELF, hardware deploy или тестов на устройстве в ходе аудита **не выполнялось**. Данные build202 подтверждают проблему, а шаги выше пока являются инженерными гипотезами и планом их проверки.
