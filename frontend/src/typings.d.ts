// Minimal Node.js type declarations for browser build
// These are needed because @supabase/storage-js includes Node types in its .d.cts file
// but we are compiling for the browser. Declare them as any to avoid errors.

type Buffer = any;

declare namespace NodeJS {
  interface ReadableStream {}
  interface WritableStream {}
  interface Process {}
}
