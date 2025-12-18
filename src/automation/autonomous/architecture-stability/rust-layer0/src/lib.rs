//! # Layer 0 Runtime - OS/Hardware Integration
//! 
//! Memory-safe, high-performance runtime for system-level operations.
//! This crate provides optimized implementations for hardware abstraction,
//! real-time control primitives, and low-level system interfaces.
//! 
//! ## Design Goals
//! - Zero-cost abstractions for real-time systems
//! - Memory safety without garbage collection
//! - Lock-free data structures for concurrent access
//! - Minimal latency for time-critical operations

use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::time::{Duration, Instant};
use thiserror::Error;

/// Error types for Layer 0 runtime operations
#[derive(Error, Debug)]
pub enum Layer0Error {
    #[error("Hardware initialization failed: {0}")]
    HardwareInitFailed(String),
    
    #[error("Real-time constraint violated: expected {expected_us}μs, got {actual_us}μs")]
    RealTimeViolation {
        expected_us: u64,
        actual_us: u64,
    },
    
    #[error("Sensor data unavailable")]
    SensorDataUnavailable,
    
    #[error("Control loop error: {0}")]
    ControlLoopError(String),
}

pub type Result<T> = std::result::Result<T, Layer0Error>;

/// Real-time statistics for performance monitoring
#[derive(Debug, Clone, Copy)]
pub struct RtStats {
    pub min_latency_us: u64,
    pub max_latency_us: u64,
    pub avg_latency_us: u64,
    pub cycles_count: u64,
    pub deadline_misses: u64,
}

impl RtStats {
    pub fn new() -> Self {
        Self {
            min_latency_us: u64::MAX,
            max_latency_us: 0,
            avg_latency_us: 0,
            cycles_count: 0,
            deadline_misses: 0,
        }
    }
    
    pub fn update(&mut self, latency_us: u64, deadline_us: u64) {
        self.min_latency_us = self.min_latency_us.min(latency_us);
        self.max_latency_us = self.max_latency_us.max(latency_us);
        self.avg_latency_us = 
            (self.avg_latency_us * self.cycles_count + latency_us) / (self.cycles_count + 1);
        self.cycles_count += 1;
        
        if latency_us > deadline_us {
            self.deadline_misses += 1;
        }
    }
}

impl Default for RtStats {
    fn default() -> Self {
        Self::new()
    }
}

/// Lock-free sensor data buffer for real-time access
pub struct SensorBuffer<T: Copy> {
    data: parking_lot::RwLock<T>,
    timestamp: AtomicU64,
    valid: AtomicBool,
}

impl<T: Copy + Default> SensorBuffer<T> {
    pub fn new() -> Self {
        Self {
            data: parking_lot::RwLock::new(T::default()),
            timestamp: AtomicU64::new(0),
            valid: AtomicBool::new(false),
        }
    }
    
    /// Write sensor data (writer side)
    pub fn write(&self, data: T, timestamp_us: u64) {
        *self.data.write() = data;
        self.timestamp.store(timestamp_us, Ordering::Release);
        self.valid.store(true, Ordering::Release);
    }
    
    /// Read sensor data (reader side)
    pub fn read(&self) -> Option<(T, u64)> {
        if !self.valid.load(Ordering::Acquire) {
            return None;
        }
        
        let data = *self.data.read();
        let timestamp = self.timestamp.load(Ordering::Acquire);
        Some((data, timestamp))
    }
    
    /// Check if data is available
    pub fn is_valid(&self) -> bool {
        self.valid.load(Ordering::Acquire)
    }
}

impl<T: Copy + Default> Default for SensorBuffer<T> {
    fn default() -> Self {
        Self::new()
    }
}

/// PID Controller optimized for real-time control
#[derive(Debug, Clone, Copy)]
pub struct PidController {
    kp: f64,
    ki: f64,
    kd: f64,
    output_limit: f64,
    integral: f64,
    previous_error: f64,
}

impl PidController {
    pub fn new(kp: f64, ki: f64, kd: f64, output_limit: f64) -> Self {
        Self {
            kp,
            ki,
            kd,
            output_limit,
            integral: 0.0,
            previous_error: 0.0,
        }
    }
    
    /// Compute PID output
    pub fn compute(&mut self, setpoint: f64, measured: f64, dt: f64) -> f64 {
        let error = setpoint - measured;
        self.integral += error * dt;
        
        // Anti-windup
        self.integral = self.integral.clamp(-self.output_limit, self.output_limit);
        
        let derivative = if dt > 0.0 {
            (error - self.previous_error) / dt
        } else {
            0.0
        };
        
        self.previous_error = error;
        
        let output = self.kp * error + self.ki * self.integral + self.kd * derivative;
        output.clamp(-self.output_limit, self.output_limit)
    }
    
    /// Reset controller state
    pub fn reset(&mut self) {
        self.integral = 0.0;
        self.previous_error = 0.0;
    }
}

/// High-resolution timer for real-time control
pub struct RtTimer {
    start: Instant,
    period: Duration,
    stats: parking_lot::Mutex<RtStats>,
}

impl RtTimer {
    pub fn new(frequency_hz: u32) -> Self {
        let period_us = 1_000_000 / frequency_hz as u64;
        Self {
            start: Instant::now(),
            period: Duration::from_micros(period_us),
            stats: parking_lot::Mutex::new(RtStats::new()),
        }
    }
    
    /// Wait for next cycle (busy-wait for precision)
    pub fn wait_next_cycle(&mut self) -> Result<()> {
        let cycle_start = Instant::now();
        let elapsed = cycle_start.duration_since(self.start);
        
        // Calculate next cycle boundary
        let period_nanos = self.period.as_nanos() as u64;
        let elapsed_nanos = elapsed.as_nanos() as u64;
        let remainder = elapsed_nanos % period_nanos;
        let next_cycle = Duration::from_nanos(period_nanos - remainder);
        
        // Busy-wait for the remaining time (more accurate than sleep)
        let target = Instant::now() + next_cycle;
        while Instant::now() < target {
            std::hint::spin_loop();
        }
        
        let actual_delay = Instant::now().duration_since(cycle_start);
        let latency_us = actual_delay.as_micros() as u64;
        let deadline_us = self.period.as_micros() as u64;
        
        self.stats.lock().update(latency_us, deadline_us);
        
        if latency_us > deadline_us {
            return Err(Layer0Error::RealTimeViolation {
                expected_us: deadline_us,
                actual_us: latency_us,
            });
        }
        
        Ok(())
    }
    
    /// Get performance statistics
    pub fn get_stats(&self) -> RtStats {
        *self.stats.lock()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pid_controller() {
        let mut pid = PidController::new(1.0, 0.1, 0.05, 10.0);
        
        // Test setpoint tracking
        let output = pid.compute(5.0, 0.0, 0.01);
        assert!(output > 0.0, "Output should be positive for positive error");
        assert!(output <= 10.0, "Output should respect limits");
    }
    
    #[test]
    fn test_sensor_buffer() {
        let buffer = SensorBuffer::<f64>::new();
        assert!(!buffer.is_valid());
        
        buffer.write(42.0, 1000);
        assert!(buffer.is_valid());
        
        let (data, ts) = buffer.read().unwrap();
        assert_eq!(data, 42.0);
        assert_eq!(ts, 1000);
    }
    
    #[test]
    fn test_rt_stats() {
        let mut stats = RtStats::new();
        
        stats.update(100, 1000);
        assert_eq!(stats.cycles_count, 1);
        assert_eq!(stats.deadline_misses, 0);
        
        stats.update(2000, 1000);
        assert_eq!(stats.cycles_count, 2);
        assert_eq!(stats.deadline_misses, 1);
    }
}
