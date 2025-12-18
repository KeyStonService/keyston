/**
 * @file system_hal.c
 * @brief Layer 0 (OS/Hardware) HAL Implementation
 * 
 * Platform-specific implementation of hardware abstraction layer.
 * This is a reference implementation for Linux/POSIX systems.
 * 
 * @author Unmanned Island Team
 * @version 1.0.0
 * @license MIT
 */

#include "system_hal.h"
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#if defined(__linux__)
    #include <sys/mman.h>
    #define HAS_CLOCK_MONOTONIC_RAW 1
#endif

/* ============================================================================
 * Platform Detection
 * ============================================================================ */

#if defined(__x86_64__) || defined(__i386__)
    #define ARCH_X86 1
    #include <x86intrin.h>
#elif defined(__aarch64__) || defined(__arm__)
    #define ARCH_ARM 1
#endif

/* ============================================================================
 * Static Data
 * ============================================================================ */

static struct {
    bool initialized;
    hal_timestamp_us_t start_time_us;
} g_hal_state = { .initialized = false };

/* ============================================================================
 * Private Functions
 * ============================================================================ */

static void hal_initialize(void) __attribute__((unused));

static void hal_initialize(void) {
    if (g_hal_state.initialized) {
        return;
    }
    
    g_hal_state.start_time_us = hal_get_timestamp_us();
    g_hal_state.initialized = true;
}

/* ============================================================================
 * Timing Functions Implementation
 * ============================================================================ */

hal_timestamp_us_t hal_get_timestamp_us(void) {
    struct timespec ts;
    
#if HAS_CLOCK_MONOTONIC_RAW
    /* Use CLOCK_MONOTONIC_RAW for unaffected by NTP adjustments */
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &ts) == 0) {
        return (hal_timestamp_us_t)ts.tv_sec * 1000000ULL + 
               (hal_timestamp_us_t)ts.tv_nsec / 1000ULL;
    }
#endif
    
    /* Fallback to CLOCK_MONOTONIC */
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return (hal_timestamp_us_t)ts.tv_sec * 1000000ULL + 
               (hal_timestamp_us_t)ts.tv_nsec / 1000ULL;
    }
    
    /* Fallback failed, return 0 */
    return 0;
}

void hal_delay_us(uint32_t delay_us) {
    const hal_timestamp_us_t start = hal_get_timestamp_us();
    const hal_timestamp_us_t end = start + delay_us;
    
    /* For delays > 10ms, use nanosleep to avoid CPU burn */
    if (delay_us > 10000) {
        struct timespec req = {
            .tv_sec = delay_us / 1000000,
            .tv_nsec = (delay_us % 1000000) * 1000
        };
        nanosleep(&req, NULL);
    } else {
        /* Busy-wait for short delays (more accurate) */
        while (hal_get_timestamp_us() < end) {
            hal_spin_hint();
        }
    }
}

void hal_delay_ns(uint32_t delay_ns) {
    /* For nanosecond delays, always busy-wait */
    const uint64_t cycles_per_ns = 2; /* Assume ~2 GHz CPU */
    const uint64_t target_cycles = hal_get_cycle_count() + (delay_ns * cycles_per_ns);
    
    while (hal_get_cycle_count() < target_cycles) {
        hal_spin_hint();
    }
}

/* ============================================================================
 * Timer Functions Implementation
 * ============================================================================ */

hal_status_t hal_timer_init(uint8_t timer_id __attribute__((unused)), 
                            const hal_timer_config_t* config) {
    if (config == NULL) {
        return HAL_INVALID_PARAM;
    }
    
    /* TODO: Implement platform-specific timer initialization */
    /* This would interact with hardware timers on embedded systems */
    
    return HAL_OK;
}

hal_status_t hal_timer_start(uint8_t timer_id __attribute__((unused))) {
    /* TODO: Implement platform-specific timer start */
    return HAL_OK;
}

hal_status_t hal_timer_stop(uint8_t timer_id __attribute__((unused))) {
    /* TODO: Implement platform-specific timer stop */
    return HAL_OK;
}

hal_status_t hal_timer_get_counter(uint8_t timer_id __attribute__((unused)), 
                                   uint32_t* counter) {
    if (counter == NULL) {
        return HAL_INVALID_PARAM;
    }
    
    /* TODO: Implement platform-specific counter read */
    *counter = 0;
    return HAL_OK;
}

/* ============================================================================
 * Memory Functions Implementation
 * ============================================================================ */

void* hal_malloc_aligned(size_t size, size_t alignment) {
    void* ptr = NULL;
    
#if defined(_POSIX_C_SOURCE) && _POSIX_C_SOURCE >= 200112L
    if (posix_memalign(&ptr, alignment, size) != 0) {
        return NULL;
    }
#else
    /* Fallback: allocate extra space for alignment */
    void* raw = malloc(size + alignment + sizeof(void*));
    if (raw == NULL) {
        return NULL;
    }
    
    /* Align pointer */
    uintptr_t addr = (uintptr_t)raw + sizeof(void*);
    uintptr_t aligned = (addr + alignment - 1) & ~(alignment - 1);
    ptr = (void*)aligned;
    
    /* Store original pointer for free */
    *((void**)aligned - 1) = raw;
#endif
    
    return ptr;
}

void hal_free_aligned(void* ptr) {
    if (ptr == NULL) {
        return;
    }
    
#if defined(_POSIX_C_SOURCE) && _POSIX_C_SOURCE >= 200112L
    free(ptr);
#else
    /* Retrieve original pointer */
    void* raw = *((void**)ptr - 1);
    free(raw);
#endif
}

void hal_cache_flush(const void* addr, size_t size) {
    /* Ensure all writes complete before DMA */
    hal_memory_barrier();
    
#if defined(__linux__)
    /* On Linux, we can use msync for memory-mapped regions */
    msync((void*)addr, size, MS_SYNC);
#elif ARCH_ARM
    /* ARM-specific cache flush */
    __builtin___clear_cache((char*)addr, (char*)addr + size);
#endif
    
    hal_dmb();
}

void hal_cache_invalidate(void* addr __attribute__((unused)), 
                          size_t size __attribute__((unused))) {
    /* Ensure cache coherency after DMA */
    hal_dmb();
    
#if ARCH_ARM
    /* ARM-specific cache invalidate */
    __builtin___clear_cache((char*)addr, (char*)addr + size);
#endif
    
    hal_memory_barrier();
}

/* ============================================================================
 * DMA Functions Implementation
 * ============================================================================ */

hal_status_t hal_dma_init(uint8_t dma_id __attribute__((unused)), 
                          const hal_dma_config_t* config) {
    if (config == NULL) {
        return HAL_INVALID_PARAM;
    }
    
    /* TODO: Implement platform-specific DMA initialization */
    return HAL_OK;
}

hal_status_t hal_dma_start(uint8_t dma_id __attribute__((unused))) {
    /* TODO: Implement platform-specific DMA start */
    return HAL_OK;
}

hal_status_t hal_dma_wait(uint8_t dma_id __attribute__((unused)), 
                          uint32_t timeout_us) {
    /* TODO: Implement platform-specific DMA wait */
    if (timeout_us > 0) {
        hal_delay_us(timeout_us);
    }
    return HAL_OK;
}

/* ============================================================================
 * Interrupt Functions Implementation
 * ============================================================================ */

static uint32_t g_interrupt_nesting = 0;

uint32_t hal_disable_interrupts(void) {
    /* On userspace Linux, we can't disable interrupts */
    /* Return current nesting level as "state" */
    return g_interrupt_nesting++;
}

void hal_restore_interrupts(uint32_t state __attribute__((unused))) {
    if (g_interrupt_nesting > 0) {
        g_interrupt_nesting--;
    }
}

void hal_enter_critical(void) {
    hal_disable_interrupts();
}

void hal_exit_critical(void) {
    hal_restore_interrupts(0);
}

/* ============================================================================
 * Utility Functions Implementation
 * ============================================================================ */

uint64_t hal_get_cycle_count(void) {
#if ARCH_X86
    /* Use RDTSC on x86/x64 */
    return __rdtsc();
#elif ARCH_ARM && defined(__aarch64__)
    /* Use virtual counter on ARM64 */
    uint64_t val;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r"(val));
    return val;
#else
    /* Fallback: use timestamp in nanoseconds */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
#endif
}
