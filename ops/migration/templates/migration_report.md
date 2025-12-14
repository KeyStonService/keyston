# 遷移報告模板

## 基本資訊

- **遷移方向**: {{ direction }}
- **執行時間**: {{ timestamp }}
- **狀態**: {{ status }}
- **備份路徑**: {{ backup_path }}

## 遷移摘要

- **處理的檔案數**: {{ file_count }}
- **成功**: {{ success_count }}
- **失敗**: {{ error_count }}

## 處理的檔案

| 來源 | 目標 | 狀態 |
|------|------|------|
{{ file_table }}

## 配置變更

### drone-config.yml 變更

{{ drone_config_changes }}

### island-control.yml 變更

{{ island_config_changes }}

## 需要手動處理的項目

{{ manual_items }}

## 驗證結果

{{ validation_results }}

## 遷移日誌

```
{{ migration_log }}
```

## 回滾指引

如需回滾，請執行：

```bash
# 還原備份
cp -r {{ backup_path }}/* {{ target_path }}/

# 或使用遷移工具
python3 migration/migrator.py --direction={{ reverse_direction }}
```

---

*報告生成於 {{ timestamp }}*
