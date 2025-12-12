# Profiling Recipes

| Stack           | 工具                         | 命令                                            |
| --------------- | ---------------------------- | ----------------------------------------------- |
| Rust            | `cargo flamegraph`, `perf`   | `cargo flamegraph --root`                       |
| Go              | pprof, `go test -cpuprofile` | `go test -run Test -cpuprofile cpu.out`         |
| TypeScript/Node | Clinic.js, 0x                | `npx clinic flame -- node app.js`               |
| Python          | py-spy, scalene              | `py-spy record -o profile.svg -- python app.py` |
| Java            | async-profiler               | `./profiler.sh -d 30 -f out.svg <pid>`          |

> 建議將輸出上傳至 `reports/performance/`，並在 capacity-planning.md 摘要。
