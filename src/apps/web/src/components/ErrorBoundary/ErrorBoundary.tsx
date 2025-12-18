/**
 * Error Boundary Component
 * Catches React errors in the component tree and displays a fallback UI
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

const isDevelopment = process.env.NODE_ENV !== 'production';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary Component
 * Wraps components to catch and handle errors gracefully
 *
 * @example
 * ```tsx
 * <ErrorBoundary fallback={<ErrorFallback />}>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    if (isDevelopment) {
      console.error('ErrorBoundary caught an error:', error);
      console.error('Error info:', errorInfo);
    }

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you might want to log to an error reporting service
    // Example: logErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return <ErrorFallback error={this.state.error} onReset={this.handleReset} />;
    }

    return this.props.children;
  }
}

/**
 * Default Error Fallback Component
 */
interface ErrorFallbackProps {
  error: Error | null;
  onReset: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, onReset }) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '20px',
        backgroundColor: '#0a0a0a',
        color: '#ffffff',
      }}
    >
      <div
        style={{
          maxWidth: '600px',
          textAlign: 'center',
        }}
      >
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#ef4444' }}>
          ⚠️ Something went wrong
        </h1>
        <p style={{ fontSize: '1.125rem', marginBottom: '2rem', color: '#a1a1aa' }}>
          We're sorry, but an unexpected error occurred. Please try refreshing the page or contact
          support if the problem persists.
        </p>

        {isDevelopment && error && (
          <details
            style={{
              marginBottom: '2rem',
              padding: '1rem',
              backgroundColor: '#1a1a1a',
              borderRadius: '8px',
              textAlign: 'left',
              border: '1px solid #27272a',
            }}
          >
            <summary
              style={{
                cursor: 'pointer',
                fontWeight: 'bold',
                marginBottom: '0.5rem',
                color: '#ef4444',
              }}
            >
              Error Details (Development Only)
            </summary>
            <pre
              style={{
                fontSize: '0.875rem',
                overflow: 'auto',
                color: '#fca5a5',
              }}
            >
              {error.message}
            </pre>
            {error.stack && (
              <pre
                style={{
                  fontSize: '0.75rem',
                  overflow: 'auto',
                  marginTop: '0.5rem',
                  color: '#a1a1aa',
                }}
              >
                {error.stack}
              </pre>
            )}
          </details>
        )}

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <button
            onClick={onReset}
            style={{
              padding: '0.75rem 1.5rem',
              fontSize: '1rem',
              fontWeight: '600',
              color: '#ffffff',
              backgroundColor: '#3b82f6',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'background-color 0.2s',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#2563eb')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#3b82f6')}
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              fontSize: '1rem',
              fontWeight: '600',
              color: '#ffffff',
              backgroundColor: '#71717a',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'background-color 0.2s',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#52525b')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#71717a')}
          >
            Reload Page
          </button>
        </div>
      </div>
    </div>
  );
};
