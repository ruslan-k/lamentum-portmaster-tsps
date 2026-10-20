/* Host test for lc2_input_latch.h. Pure logic, no device and no SDL. */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "lc2_input_latch.h"

#define A_BIT (1ULL << 0)

static struct lc2_input_latch fresh(long forced) {
    struct lc2_input_latch s;
    memset(&s, 0, sizeof s);
    s.configured = 1;
    s.forced = forced;
    return s;
}

static void tap_shorter_than_frame_survives(void) {
    /* 60 fps-ish guest: floor window applies, tap of 40 ms still reaches the guest. */
    struct lc2_input_latch s = fresh(-1);
    assert(lc2_input_latch_apply(&s, 0, 0, 0) == 0);
    assert(lc2_input_latch_apply(&s, 10, 0, A_BIT) == A_BIT);
    assert(lc2_input_latch_apply(&s, 50, 0, 0) == A_BIT);       /* released, still visible */
    assert(lc2_input_latch_apply(&s, 100, 0, 0) == A_BIT);
    assert(lc2_input_latch_apply(&s, 200, 0, 0) == 0);           /* window expired */
}

static void slow_guest_extends_window_to_one_frame(void) {
    /* Frames every 600 ms: a 100 ms tap must survive until the next frame boundary. */
    struct lc2_input_latch s = fresh(-1);
    lc2_input_latch_apply(&s, 1000, 1, 0);      /* frame 1 presented */
    lc2_input_latch_apply(&s, 1600, 2, 0);      /* frame 2, interval measured 600 ms */
    assert(s.interval == 600);
    assert(lc2_input_latch_apply(&s, 1610, 2, A_BIT) == A_BIT);
    assert(lc2_input_latch_apply(&s, 1710, 2, 0) == A_BIT);      /* released after 100 ms */
    assert(lc2_input_latch_apply(&s, 2270, 3, 0) == A_BIT);      /* still inside the window */
    assert(lc2_input_latch_apply(&s, 2400, 3, 0) == 0);          /* window closed */
}

static void no_stuck_bit(void) {
    struct lc2_input_latch s = fresh(200);
    assert(lc2_input_latch_apply(&s, 0, 0, A_BIT) == A_BIT);
    assert(lc2_input_latch_apply(&s, 100000, 0, 0) == 0);
    assert(s.active == 0);
}

static void held_button_is_not_extended_after_release(void) {
    struct lc2_input_latch s = fresh(300);
    for (uint64_t t = 0; t <= 1000; t += 8)
        assert(lc2_input_latch_apply(&s, t, 0, A_BIT) == A_BIT); /* held */
    assert(lc2_input_latch_apply(&s, 1008, 0, 0) == A_BIT);      /* deadline refreshed at 1000 */
    assert(lc2_input_latch_apply(&s, 1290, 0, 0) == A_BIT);
    assert(lc2_input_latch_apply(&s, 1310, 0, 0) == 0);
}

static void zero_window_disables(void) {
    struct lc2_input_latch s = fresh(0);
    assert(lc2_input_latch_apply(&s, 0, 0, A_BIT) == A_BIT);
    assert(lc2_input_latch_apply(&s, 8, 0, 0) == 0);
}

static void ceiling_clamps_forced_window(void) {
    struct lc2_input_latch s = fresh(-1);
    s.configured = 0;
    setenv("LC2_INPUT_MIN_HOLD_MS", "5000", 1);
    lc2_input_latch_apply(&s, 0, 0, 0);
    assert(s.forced == (long)LC2_INPUT_LATCH_CEIL_MS);
    unsetenv("LC2_INPUT_MIN_HOLD_MS");
}

static void independent_bits_do_not_leak(void) {
    struct lc2_input_latch s = fresh(250);
    uint64_t a = 1ULL << 0, b = 1ULL << 1;
    assert(lc2_input_latch_apply(&s, 0, 0, a) == a);
    assert(lc2_input_latch_apply(&s, 10, 0, b) == (a | b));      /* a released, still latched */
    assert(lc2_input_latch_apply(&s, 60, 0, 0) == (a | b));      /* both latched */
    uint64_t later = lc2_input_latch_apply(&s, 400, 0, 0);
    assert(later == 0);
}

int main(void) {
    tap_shorter_than_frame_survives();
    slow_guest_extends_window_to_one_frame();
    no_stuck_bit();
    held_button_is_not_extended_after_release();
    zero_window_disables();
    ceiling_clamps_forced_window();
    independent_bits_do_not_leak();
    puts("input-latch: 7 checks OK");
    return 0;
}
