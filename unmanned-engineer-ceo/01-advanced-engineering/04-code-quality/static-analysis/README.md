# Static Analysis Configuration

| Stack      | 工具                 | 命令                         | 備註                       |
| ---------- | -------------------- | ---------------------------- | -------------------------- |
| TypeScript | ESLint (flat config) | `npm run lint -w <pkg>`      | 覆蓋 core/_, apps/_        |
| Python     | Ruff + Pyright       | `ruff check`, `pyright`      | automation/, tools/        |
| Go         | golangci-lint        | `golangci-lint run ./...`    | services/, infrastructure/ |
| Rust       | clippy + cargo fmt   | `cargo clippy --all-targets` | agents/ (Rust modules)     |

> 對應設定檔請放置於各 workspace 根目錄，並在此列出檔案位置與版本要求。
