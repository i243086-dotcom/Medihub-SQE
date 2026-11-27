# Archived initial series

The official portable executable ran the same workloads and matched the installed executable's SHA-256. L01 and L02 completed and passed. L03 did not reach steady state. Its first login returned 200, the next exceeded the original two-second setup timeout, and the CLI exited 107. The native dashboard was reachable, while the final HTML export was absent for this interrupted scenario.

The runner then stopped while preparing L04. The actual runner error was `OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted`. No L04 k6 process was started. Windows showed loopback sockets in TIME_WAIT. The final runner checks for a live listener and uses a longer timeout for synthetic setup logins, leaving measured request behavior unchanged.

- [L01 run record](P5-L01/run.json) and [native console](P5-L01/console.log)
- [L02 run record](P5-L02/run.json) and [native console](P5-L02/console.log)
- [Aborted L03 run record](P5-L03/run.json) and [native console](P5-L03/console.log)
- [Initial-series database safety](database-safety.json)
- [Final series and provenance](../README.md)
