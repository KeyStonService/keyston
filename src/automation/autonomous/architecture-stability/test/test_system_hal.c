/**
 * @file test_system_hal.c
 * @brief Unit tests for Layer 0 HAL
 */

#include "../system_hal.h"
#include <stdio.h>
#include <assert.h>
#include <string.h>

#define TEST_PASS() printf("  ✓ %s\n", __func__)
#define TEST_FAIL(msg) do { \
    printf("  ✗ %s: %s\n", __func__, msg); \
    return 1; \
} while(0)

/* Test timing functions */
static int test_timestamp(void) {
    hal_timestamp_us_t t1 = hal_get_timestamp_us();
    hal_delay_us(1000); /* 1ms delay */
    hal_timestamp_us_t t2 = hal_get_timestamp_us();
    
    uint64_t diff = t2 - t1;
    if (diff < 900 || diff > 1100) {
        TEST_FAIL("Timestamp delta out of range");
    }
    
    TEST_PASS();
    return 0;
}

/* Test aligned memory allocation */
static int test_aligned_malloc(void) {
    const size_t alignment = 64;
    void* ptr = hal_malloc_aligned(1024, alignment);
    
    if (ptr == NULL) {
        TEST_FAIL("Aligned malloc returned NULL");
    }
    
    /* Check alignment */
    if (((uintptr_t)ptr % alignment) != 0) {
        hal_free_aligned(ptr);
        TEST_FAIL("Pointer not aligned");
    }
    
    /* Test writing to allocated memory */
    memset(ptr, 0xAA, 1024);
    
    hal_free_aligned(ptr);
    TEST_PASS();
    return 0;
}

/* Test cycle counter */
static int test_cycle_counter(void) {
    uint64_t c1 = hal_get_cycle_count();
    
    /* Do some work */
    volatile int sum = 0;
    for (int i = 0; i < 1000; i++) {
        sum += i;
    }
    
    uint64_t c2 = hal_get_cycle_count();
    
    if (c2 <= c1) {
        TEST_FAIL("Cycle counter not increasing");
    }
    
    TEST_PASS();
    return 0;
}

/* Test interrupt control */
static int test_interrupt_control(void) {
    uint32_t state = hal_disable_interrupts();
    hal_restore_interrupts(state);
    
    hal_enter_critical();
    hal_exit_critical();
    
    TEST_PASS();
    return 0;
}

/* Test memory barriers */
static int test_memory_barriers(void) {
    volatile int x = 0;
    
    x = 42;
    hal_memory_barrier();
    
    if (x != 42) {
        TEST_FAIL("Memory barrier failed");
    }
    
    hal_dmb();
    
    TEST_PASS();
    return 0;
}

/* Main test runner */
int main(void) {
    int failures = 0;
    
    printf("Running Layer 0 HAL tests...\n\n");
    
    failures += test_timestamp();
    failures += test_aligned_malloc();
    failures += test_cycle_counter();
    failures += test_interrupt_control();
    failures += test_memory_barriers();
    
    printf("\n");
    if (failures == 0) {
        printf("All tests passed! ✓\n");
        return 0;
    } else {
        printf("%d test(s) failed! ✗\n", failures);
        return 1;
    }
}
