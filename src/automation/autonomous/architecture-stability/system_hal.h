/**
 * @file system_hal.h
 * @brief Layer 0 (OS/Hardware) Hardware Abstraction Layer
 * 
 * Low-level C interface for system-level operations including:
 * - High-precision timing
 * - Memory-mapped I/O
 * - Interrupt handling
 * - DMA operations
 * 
 * Language: C (for maximum portability and low-level access)
 * 
 * @author Unmanned Island Team
 * @version 1.0.0
 * @license MIT
 */

#ifndef SYSTEM_HAL_H
#define SYSTEM_HAL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * Type Definitions
 * ============================================================================ */

/**
 * @brief Return codes for HAL operations
 */
typedef enum {
    HAL_OK = 0,           /**< Operation successful */
    HAL_ERROR = -1,       /**< Generic error */
    HAL_TIMEOUT = -2,     /**< Operation timed out */
    HAL_BUSY = -3,        /**< Resource busy */
    HAL_INVALID_PARAM = -4 /**< Invalid parameter */
} hal_status_t;

/**
 * @brief High-precision timestamp in microseconds
 */
typedef uint64_t hal_timestamp_us_t;

/**
 * @brief Hardware timer configuration
 */
typedef struct {
    uint32_t frequency_hz;  /**< Timer frequency in Hz */
    bool enable_interrupt;  /**< Enable timer interrupt */
    void (*callback)(void*); /**< Optional callback function */
    void* user_data;        /**< User data for callback */
} hal_timer_config_t;

/**
 * @brief DMA transfer configuration
 */
typedef struct {
    void* src_addr;         /**< Source address */
    void* dst_addr;         /**< Destination address */
    size_t transfer_size;   /**< Transfer size in bytes */
    bool circular;          /**< Circular mode enable */
} hal_dma_config_t;

/* ============================================================================
 * Timing Functions
 * ============================================================================ */

/**
 * @brief Get current timestamp in microseconds
 * @return Current timestamp
 */
hal_timestamp_us_t hal_get_timestamp_us(void);

/**
 * @brief High-precision delay in microseconds
 * @param delay_us Delay duration in microseconds
 */
void hal_delay_us(uint32_t delay_us);

/**
 * @brief High-precision delay in nanoseconds (busy-wait)
 * @param delay_ns Delay duration in nanoseconds
 */
void hal_delay_ns(uint32_t delay_ns);

/* ============================================================================
 * Timer Functions
 * ============================================================================ */

/**
 * @brief Initialize hardware timer
 * @param timer_id Timer peripheral ID (0-based)
 * @param config Timer configuration
 * @return HAL_OK on success, error code otherwise
 */
hal_status_t hal_timer_init(uint8_t timer_id, const hal_timer_config_t* config);

/**
 * @brief Start hardware timer
 * @param timer_id Timer peripheral ID
 * @return HAL_OK on success, error code otherwise
 */
hal_status_t hal_timer_start(uint8_t timer_id);

/**
 * @brief Stop hardware timer
 * @param timer_id Timer peripheral ID
 * @return HAL_OK on success, error code otherwise
 */
hal_status_t hal_timer_stop(uint8_t timer_id);

/**
 * @brief Get timer counter value
 * @param timer_id Timer peripheral ID
 * @param counter Output pointer for counter value
 * @return HAL_OK on success, error code otherwise
 */
hal_status_t hal_timer_get_counter(uint8_t timer_id, uint32_t* counter);

/* ============================================================================
 * Memory Functions
 * ============================================================================ */

/**
 * @brief Allocate cache-aligned memory
 * @param size Size in bytes
 * @param alignment Alignment requirement (must be power of 2)
 * @return Pointer to aligned memory, NULL on failure
 */
void* hal_malloc_aligned(size_t size, size_t alignment);

/**
 * @brief Free aligned memory
 * @param ptr Pointer to free
 */
void hal_free_aligned(void* ptr);

/**
 * @brief Flush data cache for DMA coherency
 * @param addr Start address
 * @param size Size in bytes
 */
void hal_cache_flush(const void* addr, size_t size);

/**
 * @brief Invalidate data cache for DMA coherency
 * @param addr Start address
 * @param size Size in bytes
 */
void hal_cache_invalidate(void* addr, size_t size);

/* ============================================================================
 * DMA Functions
 * ============================================================================ */

/**
 * @brief Initialize DMA controller
 * @param dma_id DMA channel ID
 * @param config DMA configuration
 * @return HAL_OK on success, error code otherwise
 */
hal_status_t hal_dma_init(uint8_t dma_id, const hal_dma_config_t* config);

/**
 * @brief Start DMA transfer
 * @param dma_id DMA channel ID
 * @return HAL_OK on success, error code otherwise
 */
hal_status_t hal_dma_start(uint8_t dma_id);

/**
 * @brief Wait for DMA completion
 * @param dma_id DMA channel ID
 * @param timeout_us Timeout in microseconds (0 for no timeout)
 * @return HAL_OK on success, HAL_TIMEOUT on timeout
 */
hal_status_t hal_dma_wait(uint8_t dma_id, uint32_t timeout_us);

/* ============================================================================
 * Interrupt Functions
 * ============================================================================ */

/**
 * @brief Disable interrupts globally
 * @return Previous interrupt state (for restoration)
 */
uint32_t hal_disable_interrupts(void);

/**
 * @brief Restore interrupts to previous state
 * @param state Previous interrupt state from hal_disable_interrupts()
 */
void hal_restore_interrupts(uint32_t state);

/**
 * @brief Enter critical section (disable interrupts)
 */
void hal_enter_critical(void);

/**
 * @brief Exit critical section (restore interrupts)
 */
void hal_exit_critical(void);

/* ============================================================================
 * Utility Functions
 * ============================================================================ */

/**
 * @brief Get CPU cycle counter (for profiling)
 * @return Current CPU cycle count
 */
uint64_t hal_get_cycle_count(void);

/**
 * @brief Spin loop hint (for busy-wait optimization)
 */
static inline void hal_spin_hint(void) {
    #if defined(__x86_64__) || defined(__i386__)
        __asm__ volatile("pause");
    #elif defined(__aarch64__) || defined(__arm__)
        __asm__ volatile("yield");
    #else
        /* Generic NOP */
        __asm__ volatile("nop");
    #endif
}

/**
 * @brief Compiler memory barrier
 */
static inline void hal_memory_barrier(void) {
    __asm__ volatile("" ::: "memory");
}

/**
 * @brief Data memory barrier (ensure memory operations complete)
 */
static inline void hal_dmb(void) {
    #if defined(__aarch64__) || defined(__arm__)
        __asm__ volatile("dmb sy" ::: "memory");
    #else
        __sync_synchronize();
    #endif
}

#ifdef __cplusplus
}
#endif

#endif /* SYSTEM_HAL_H */
