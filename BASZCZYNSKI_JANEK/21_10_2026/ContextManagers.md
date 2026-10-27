# Context Managers: Resource Lifecycle and Exception Guarantees

## 1. The Core Problem: The Resource Lifecycle

Every external or system resource follows a three-phase lifecycle:

1. **Acquire**: Open a file descriptor, open a database connection, create a scratch directory, or change working directory.
2. **Use**: Read, write, compute, or mutate application state.
3. **Release**: Close the file or connection, commit or rollback transactions, restore original directories/environment variables.

### The Risk

When an exception or early return occurs in the **Use** step, the **Release** step is frequently bypassed in naive code. This causes resource leaks, file locks, dangling network sockets, and corrupted application state.

---

## 2. Anatomy of the `with` Statement

A context manager formalises resource boundaries by enforcing execution before and after a designated block:

```text
    manager = ContextManager()
    value = manager.__enter__()
    try:
        ... body statements ...
    except Exception as exc:
        if not manager.__exit__(type(exc), exc, exc.__traceback__):
            raise
    else:
        manager.__exit__(None, None, None)
```
