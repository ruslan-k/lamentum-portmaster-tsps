"""Page/cursor oracle: one frame in, (page, cursor row) out.

Geometry is the measured main-menu signature of this title: four text rows and a
highlight band in x 88..124 whose y names the selected entry. The oracle is
deliberately conservative - it returns UNKNOWN with a reason rather than guessing
a page, because a wrong page silently turns a "New Game" press into "Credits".

Thresholds here are for self-authored frames; a real capture is needed to
calibrate them, and that calibration is recorded separately. Nothing in this
module reads game data.
"""
MAIN_MENU = 'MAIN_MENU'
UNKNOWN = 'UNKNOWN'

# Measured on a live frame of this build (evidence/nav-oracle-01): the list sits
# in the lower-left region, text starts near x 140, and the SELECTION is a bright
# cursor glyph to the LEFT of the row (x 40..120), not a full-width band.
CURSOR_X = (40, 120)
TEXT_X = (140, 340)
MENU_TOP, MENU_BOTTOM = 380, 660
BAND_HALF = 6
TEXT_MIN = 18.0
CURSOR_MIN = 12.0
CURSOR_MARGIN = 8.0
ROW_TOLERANCE = 30
EXPECTED_ROWS = {442: 'load', 492: 'newgame', 542: 'options', 592: 'credits'}
MAX_BAND = 60


def frame_from_rows(width, height, rows=(), cursor_y=None, text_level=70, cursor_level=235,
                    background=0):
    """Synthetic frame: text bands at `rows`, highlight band in the cursor window."""
    frame = bytearray([background]) * (width * height * 3)
    for y in rows:
        for dy in range(-BAND_HALF, BAND_HALF + 1):
            line = y + dy
            if not 0 <= line < height:
                continue
            base = line * width * 3
            for x in range(TEXT_X[0], min(TEXT_X[1], width)):
                frame[base + x * 3:base + x * 3 + 3] = bytes((text_level,) * 3)
            for x in range(CURSOR_X[0], min(CURSOR_X[1], width)):
                level = cursor_level if y == cursor_y else text_level // 2
                frame[base + x * 3:base + x * 3 + 3] = bytes((level,) * 3)
    return bytes(frame)


def _row_mean(frame, bpp, width, line, span):
    """Mean channel value of one sampled row inside a column window.

    Channel mean is used instead of luma weighting: on the synthetic frames the
    channels are equal, and a real calibration measures the threshold directly.
    """
    start = (line * width + span[0]) * bpp
    end = (line * width + min(span[1], width)) * bpp
    chunk = frame[start:end]
    return sum(chunk) / len(chunk) if chunk else 0.0


def _window_mean(frame, bpp, width, y, span, rows):
    """Mean over a horizontal band centred on sampled row `y/stride` (sampled rows)."""
    line = y
    total, count = 0.0, 0
    for sampled in range(max(0, line - BAND_HALF), min(rows, line + BAND_HALF + 1)):
        total += _row_mean(frame, bpp, width, sampled, span)
        count += 1
    return total / count if count else 0.0


def _refuse(reason, **extra):
    return {'page': UNKNOWN, 'row': None, 'cursor_y': None, 'confident': False,
            'reason': reason, **extra}


def analyse(frame, width, height, stride=1, cursor_min=CURSOR_MIN):
    if not isinstance(frame, (bytes, bytearray)) or not width or not height:
        return _refuse('no frame')
    rows = height // stride
    if not rows:
        return _refuse('no sampled rows')
    per_row = len(frame) / rows
    if per_row not in (width, width * 3):
        return _refuse('buffer size does not match %dx%d sampled by %d' % (width, height, stride))
    bpp = 3 if per_row == width * 3 else 1

    text = [_window_mean(frame, bpp, width, y, TEXT_X, rows) for y in range(rows)]
    bright = [y for y, value in enumerate(text)
              if value > TEXT_MIN and MENU_TOP <= y * stride <= MENU_BOTTOM]
    bands = []
    for y in bright:
        if bands and y - bands[-1][-1] <= 2:
            bands[-1].append(y)
        else:
            bands.append([y])
    centres = [sum(b) / len(b) * stride for b in bands]
    heights = [(b[-1] - b[0] + 1) * stride for b in bands]

    if not bands:
        return _refuse('no bright rows in the text window')
    if len(bands) == 1:
        return _refuse('single bright row (%d), not a menu' % round(centres[0]),
                       bands=len(bands), centre=round(centres[0]))
    if max(heights) > MAX_BAND:
        return _refuse('bright row taller than %d px - not a text band' % MAX_BAND,
                       bands=len(bands))

    matched = []
    for centre in centres:
        nearest = min(EXPECTED_ROWS, key=lambda y: abs(y - centre))
        if abs(nearest - centre) <= ROW_TOLERANCE:
            matched.append(nearest)
        else:
            matched.append(None)
    if len(bands) != len(EXPECTED_ROWS) or None in matched:
        return _refuse('row pitch/positions differ from the measured menu',
                       bands=len(bands), centres=[round(c) for c in centres])

    # The selection glyph is INK LEFT OF the text, not a brighter band: on the
    # measured frame the selected row reads 26.6 there while the others read 0.0,
    # and its text is dimmer than the glyph. So the row is chosen by "has a glyph"
    # (absolute level plus separation from the second best), never by contrast
    # against its own text.
    cursor_scores = [_window_mean(frame, bpp, width, round(centre / stride), CURSOR_X, rows)
                     for centre in centres]
    order = sorted(range(len(cursor_scores)), key=lambda i: cursor_scores[i], reverse=True)
    best = order[0]
    second = cursor_scores[order[1]] if len(order) > 1 else 0.0
    row = None
    cursor_y = None
    if cursor_scores[best] >= cursor_min and cursor_scores[best] - second >= CURSOR_MARGIN:
        cursor_y = round(centres[best])
        row = EXPECTED_ROWS[matched[best]]
    return {'page': MAIN_MENU, 'row': row, 'cursor_y': cursor_y,
            'confident': row is not None, 'bands': len(bands),
            'centres': [round(c) for c in centres],
            'reason': 'measured menu geometry' if row else 'page matched, no highlight band'}
