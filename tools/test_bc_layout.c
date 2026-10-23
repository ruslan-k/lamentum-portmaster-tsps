#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "zero_bc_layout.h"
#include "zero_bc.h"

static unsigned stripe_parity_cases, source_preserved_cases, guarded_buffer_cases;
static unsigned metadata_mip_cases, inplace_cases, reject_cases, selection_cases, upload_region_cases;
#define CHECK_REJECT(expr) do { assert(!(expr)); reject_cases++; } while (0)

static unsigned char *guarded_buffer(size_t bytes, unsigned char **allocation) {
    *allocation = malloc(bytes + 32);
    assert(*allocation);
    memset(*allocation, 0xa5, bytes + 32);
    return *allocation + 16;
}

static void assert_guard(const unsigned char *allocation, size_t bytes) {
    for (size_t i = 0; i < 16; i++) assert(allocation[i] == 0xa5);
    for (size_t i = bytes + 16; i < bytes + 32; i++) assert(allocation[i] == 0xa5);
}

static uint32_t next_random(uint32_t *state) {
    *state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
    return *state;
}

static void check_bc_stripe(unsigned format, unsigned w, unsigned h) {
    unsigned block_bytes = zero_bc_bytes(format);
    unsigned bpp = zero_bc_float(format) ? 16U : 4U;
    struct zero_bc_level m;
    struct zero_bc_stripe_geometry plan;
    assert(block_bytes == 8 || block_bytes == 16);
    assert(zero_bc_level_layout(w, h, block_bytes, 0, &m));
    assert(zero_bc_stripe_geometry(w, h, bpp, block_bytes, 128, &plan));

    size_t compressed = (size_t)m.blocks_x * m.blocks_y * block_bytes;
    size_t pixels = (size_t)w * h * bpp;
    assert(plan.rows == (h < 128 ? h : 128));
    assert(plan.pixel_capacity == (size_t)w * plan.rows * bpp);
    assert(plan.linear_capacity == (size_t)m.blocks_x * ((plan.rows + 3) / 4) * block_bytes);
    assert(plan.scratch_peak == plan.pixel_capacity + plan.linear_capacity);
    assert(plan.pixel_capacity <= pixels);

    unsigned char *source = malloc(compressed);
    unsigned char *source_copy = malloc(compressed);
    unsigned char *tiled_allocation = malloc(m.size + 32);
    unsigned char *full_allocation;
    unsigned char *striped_allocation;
    unsigned char *linear_full = malloc(compressed);
    assert(source && source_copy && tiled_allocation && linear_full);
    memset(tiled_allocation, 0xa5, m.size + 32);
    unsigned char *tiled = tiled_allocation + 16;
    memset(tiled, 0, m.size);
    unsigned char *full = guarded_buffer(pixels, &full_allocation);
    unsigned char *striped = guarded_buffer(pixels, &striped_allocation);

    uint32_t rng = UINT32_C(0x4d344100) ^ (format << 16) ^ (w << 1) ^ h;
    for (size_t i = 0; i < compressed; i++) source[i] = (unsigned char)(next_random(&rng) >> 24);
    memcpy(source_copy, source, compressed);
    assert(zero_bc_blocks_copy(&m, tiled, m.size, source, compressed,
                               0, 0, m.blocks_x, m.blocks_y, 1));
    assert(zero_bc_blocks_copy(&m, tiled, m.size, linear_full, compressed,
                               0, 0, m.blocks_x, m.blocks_y, 0));
    assert(zero_bc_decode(format, full, pixels, linear_full, compressed,
                          w, h, (size_t)m.blocks_x * block_bytes));

    unsigned covered_rows = 0;
    for (unsigned y = 0; y < h; y += 128) {
        unsigned rows = h - y;
        if (rows > 128) rows = 128;
        assert(y == covered_rows);
        struct zero_bc_stripe_geometry current;
        assert(zero_bc_stripe_geometry(w, rows, bpp, block_bytes, 128, &current));
        assert(current.rows == rows);
        assert(current.pixel_capacity == (size_t)w * rows * bpp);
        assert(current.pixel_capacity <= plan.pixel_capacity);
        assert(current.linear_capacity <= plan.linear_capacity);
        size_t block_rows = (rows + 3) / 4;
        size_t row_bytes = (size_t)m.blocks_x * block_rows * block_bytes;
        assert(current.linear_capacity == row_bytes);
        unsigned char *linear = malloc(row_bytes);
        assert(linear);
        assert(zero_bc_blocks_copy(&m, tiled, m.size, linear, row_bytes,
                                   0, y / 4, m.blocks_x, (unsigned)block_rows, 0));
        assert(zero_bc_decode(format, striped + (size_t)y * w * bpp,
                              current.pixel_capacity, linear, row_bytes, w, rows,
                              (size_t)m.blocks_x * block_bytes));
        covered_rows += rows;
        upload_region_cases++;
        free(linear);
    }
    assert(covered_rows == h);

    assert(memcmp(full, striped, pixels) == 0);
    assert(memcmp(source, source_copy, compressed) == 0);
    assert_guard(full_allocation, pixels);
    assert_guard(striped_allocation, pixels);
    assert_guard(tiled_allocation, m.size);
    stripe_parity_cases++;
    source_preserved_cases++;
    guarded_buffer_cases += 3;
    free(source);
    free(source_copy);
    free(tiled_allocation);
    free(full_allocation);
    free(striped_allocation);
    free(linear_full);
}

static void check_bc_mip_chain(unsigned format, unsigned width, unsigned height) {
    for (;;) {
        check_bc_stripe(format, width, height);
        if (width == 1 && height == 1) break;
        if (width > 1) width >>= 1;
        if (height > 1) height >>= 1;
    }
}

/* Large chain: validate every legal mip's metadata and checked row plan only;
 * do not allocate a full 8192x8192 RGBA decode buffer in the host fixture. */
static void check_metadata_mip_chain(unsigned format, unsigned base_width, unsigned base_height) {
    unsigned block_bytes = zero_bc_bytes(format);
    unsigned bpp = zero_bc_float(format) ? 16U : 4U;
    unsigned width = base_width, height = base_height;
    for (unsigned level = 0;; level++) {
        struct zero_bc_level mip;
        struct zero_bc_stripe_geometry plan;
        assert(zero_bc_level_layout(base_width, base_height, block_bytes, level, &mip));
        assert(mip.width == width && mip.height == height);
        assert(zero_bc_stripe_geometry(width, height, bpp, block_bytes, 128, &plan));
        assert(plan.rows == (height < 128 ? height : 128));
        assert(plan.scratch_peak == plan.pixel_capacity + plan.linear_capacity);
        metadata_mip_cases++;
        if (width == 1 && height == 1) break;
        if (width > 1) width >>= 1;
        if (height > 1) height >>= 1;
    }
}

static void check_inplace(unsigned format, unsigned width, unsigned height, unsigned seed) {
    struct zero_bc_level m;
    unsigned block_bytes = zero_bc_bytes(format);
    assert(zero_bc_level_layout(width, height, block_bytes, 0, &m));
    size_t compressed = (size_t)m.blocks_x * m.blocks_y * block_bytes;
    size_t stride = (size_t)m.blocks_x * block_bytes;
    size_t bpp = zero_bc_float(format) ? 16 : 4;
    size_t rgba = (size_t)width * height * bpp;
    size_t capacity = compressed > rgba ? compressed : rgba;
    unsigned char *source = malloc(compressed), *reference = malloc(rgba), *work = malloc(capacity + 32);
    unsigned char *tiled = calloc(m.size, 1);
    assert(source && reference && work && tiled);
    for (size_t i = 0; i < compressed; i++) source[i] = (unsigned char)(i * 37U + (i >> 8) + seed);
    assert(zero_bc_decode(format, reference, rgba, source, compressed, width, height, stride));
    assert(zero_bc_blocks_copy(&m, tiled, m.size, source, compressed, 0, 0,
                               m.blocks_x, m.blocks_y, 1));
    memset(work, 0xa5, capacity + 32);
    assert(zero_bc_blocks_copy(&m, tiled, m.size, work, capacity, 0, 0,
                               m.blocks_x, m.blocks_y, 0));
    assert(zero_bc_decode_in_place(format, work, capacity, width, height, stride));
    assert(memcmp(reference, work, rgba) == 0);
    for (size_t i = capacity; i < capacity + 32; i++) assert(work[i] == 0xa5);
    memcpy(work, source, compressed);
    assert(!zero_bc_decode_in_place(format, work, capacity - 1, width, height, stride));
    assert(!zero_bc_decode_in_place(format, work, capacity, width, height, stride + block_bytes));
    assert(memcmp(work, source, compressed) == 0);
    inplace_cases++;
    free(source); free(reference); free(work); free(tiled);
}

int main(void) {
    assert(zero_bc_should_stripe(16, 4097, 0, 0));
    assert(!zero_bc_should_stripe(16, 4096, 0, 0));
    assert(zero_bc_should_stripe(16, 1920, 0, 1));
    assert(!zero_bc_should_stripe(16, 768, 0, 1));
    assert(!zero_bc_should_stripe(16, 1920, 1, 1));
    assert(!zero_bc_should_stripe(0, 1920, 0, 1));

    size_t value = 0;
    CHECK_REJECT(zero_bc_size_mul(SIZE_MAX, 2, &value));
    CHECK_REJECT(zero_bc_size_add(SIZE_MAX, 1, &value));
    assert(zero_bc_size_mul(0, SIZE_MAX, &value) && value == 0);
    assert(zero_bc_size_add(SIZE_MAX, 0, &value) && value == SIZE_MAX);

    struct zero_bc_stripe_geometry stripe = {0};
    struct zero_bc_full_geometry full = {0};
    CHECK_REJECT(zero_bc_stripe_geometry(0, 1, 4, 16, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 0, 4, 16, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(8193, 1, 4, 16, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 8193, 4, 16, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 1, 0, 16, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 1, 3, 16, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 1, 4, 12, 128, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 1, 4, 16, 0, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 1, 4, 16, 129, &stripe));
    CHECK_REJECT(zero_bc_stripe_geometry(1, 1, 4, 16, 128, NULL));
    CHECK_REJECT(zero_bc_full_geometry(1, 1, 4, 16, 0, NULL));
    CHECK_REJECT(zero_bc_full_geometry(1, 1, 4, 16, 2, &full));
    CHECK_REJECT(zero_bc_select_stripe(16, 1024, 256, 4, 129, 0, 1, 0,
                                       &stripe, &full));

    assert(zero_bc_select_stripe(16, 1024, 64, 4, 128, 0, 1, 0,
                                 &stripe, &full) == ZERO_BC_STRIPE_FULL);
    selection_cases++;
    assert(stripe.scratch_peak == full.scratch_peak);
    assert(zero_bc_select_stripe(16, 1024, 256, 4, 128, 0, 1, 0,
                                 &stripe, &full) == ZERO_BC_STRIPE_ROWS);
    selection_cases++;
    assert(stripe.scratch_peak < full.scratch_peak);
    assert(zero_bc_select_stripe(16, 1920, 1080, 4, 128, 0, 0, 0,
                                 &stripe, &full) == ZERO_BC_STRIPE_FULL);
    selection_cases++;
    assert(zero_bc_select_stripe(16, 1920, 1080, 4, 128, 1, 1, 0,
                                 &stripe, &full) == ZERO_BC_STRIPE_FULL);
    selection_cases++;
    assert(zero_bc_select_stripe(16, 4097, 9, 4, 128, 0, 0, 0,
                                 &stripe, &full) == ZERO_BC_STRIPE_ROWS);
    selection_cases++;

    assert(zero_bc_stripe_geometry(4097, 9, 4, 16, 128, &stripe));
    assert(stripe.pixel_capacity == 147492 && stripe.linear_capacity == 49200 &&
           stripe.scratch_peak == 196692);
    assert(zero_bc_stripe_geometry(1920, 1080, 4, 16, 128, &stripe));
    assert(stripe.pixel_capacity == 983040 && stripe.linear_capacity == 245760 &&
           stripe.scratch_peak == 1228800);

    struct zero_bc_level m;
    assert(zero_bc_level_layout(8192, 4096, 16, 0, &m));
    assert(m.size == 33554432 && m.blocks_x == 2048 && m.blocks_y == 1024);
    unsigned char *seen = calloc(m.size / 16, 1); assert(seen);
    size_t checked = 0;
    for (unsigned y = 0; y < m.blocks_y; y++) for (unsigned x = 0; x < m.blocks_x; x++) {
        size_t address = zero_bc_block_address(&m, x, y);
        assert(address % 16 == 0 && address + 16 <= m.size);
        assert(!seen[address / 16]); seen[address / 16] = 1; checked++;
    }
    free(seen);
    assert(zero_bc_level_layout(8192, 8192, 16, 13, &m));
    assert(m.width == 1 && m.height == 1);
    assert(!zero_bc_level_layout(8192, 8192, 16, 14, &m));
    assert(!zero_bc_level_layout(16384, 4096, 16, 0, &m));

    const unsigned dimensions[][2] = {
        {1, 1}, {3, 5}, {7, 5}, {16, 1}, {63, 1}, {127, 129}, {128, 128},
        {129, 129}, {1023, 63}, {4096, 1}, {4097, 9}, {4097, 131},
        {1920, 1080}, {3600, 2160}, {3600, 3600}, {8192, 132}
    };
    for (size_t i = 0; i < sizeof(dimensions) / sizeof(dimensions[0]); i++) {
        check_bc_stripe(0x41, dimensions[i][0], dimensions[i][1]);
        check_bc_stripe(0x44, dimensions[i][0], dimensions[i][1]);
    }
    /* The historical target log recorded device-limit=16383, so 4097 is within
     * the observed limit; these remain host-only decoder fixtures, not a launch. */
    check_bc_mip_chain(0x41, 1920, 1080);
    check_bc_mip_chain(0x44, 1920, 1080);
    check_metadata_mip_chain(0x41, 8192, 8192);
    check_metadata_mip_chain(0x44, 8192, 8192);
    for (unsigned format = 0x41; format <= 0x50; format++) {
        if (zero_bc_bytes(format)) {
            check_bc_stripe(format, 7, 5);
            check_bc_stripe(format, 129, 129);
            check_inplace(format, 7, 5, format);
        }
    }
    check_inplace(0x44, 3600, 2160, 81);
    check_inplace(0x44, 3600, 3600, 92);

    printf("stripe geometry, full-decode parity and mip metadata OK\n");
    printf("in-place equivalence OK\n");
    printf("BC layout address uniqueness OK blocks=%zu\n", checked);
    printf("M4A_BC_FIXTURE_COUNTS stripe_parity=%u source_preserved=%u guarded_buffers=%u upload_regions=%u metadata_mips=%u inplace=%u rejects=%u selections=%u\n",
           stripe_parity_cases, source_preserved_cases, guarded_buffer_cases, upload_region_cases,
           metadata_mip_cases, inplace_cases, reject_cases, selection_cases);
    return 0;
}
