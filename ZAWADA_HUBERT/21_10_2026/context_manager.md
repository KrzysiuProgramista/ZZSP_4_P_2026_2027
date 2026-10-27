A Python context manager is an object that controls the runtime environment within a with statement.
It handles resource setup and cleanup automatically and can be implemented in two primary ways:
 - Class-based approach: Implementing the __enter__ and __exit__ magic methods.
 - Generator-based approach: Using the @contextmanager decorator from the contextlib module.
Context managers are typically used for resource management tasks such as handling database connections, temporary directories, working directories, or environment variables.   