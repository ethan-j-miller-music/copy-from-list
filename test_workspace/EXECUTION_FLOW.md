# Test Workspace Execution Flow

本目录提供一个最小化的测试场景，帮助验证 `copy_from_list.py` 在两类清单格式下的行为。以下流程假定当前工作目录位于仓库根目录。

## 1. 准备目录结构

`test_workspace/source` 下已经预置了两个示例项目：

```
ProjectAlpha/
  docs/
    design-spec.pdf
    meeting-notes.txt
  images/
    architecture.png
ProjectBeta/
  reports/
    financial-report.docx
```

可以根据需要增删文件或调整扩展名，以模拟真实业务数据。

## 2. 生成绝对路径清单

1. 执行脚本生成与当前仓库路径匹配的清单：
   ```bash
   python test_workspace/scripts/prepare_absolute_manifest.py
   ```
2. 查看输出的 `test_workspace/manifests/absolute_manifest.txt`，确认路径与 `test_workspace/source` 一致。

如需自定义，编辑 `test_workspace/manifests/absolute_manifest.template.txt` 并重新运行上述脚本即可。

## 3. Tree /F 清单

`test_workspace/manifests/tree_manifest.txt` 复制自 Windows `tree /F` 输出，已与示例目录保持同步。如对源目录结构做了改动，可在 Windows 环境重新生成 `tree /F` 清单并覆盖此文件。

## 4. 运行演练

以下命令展示 dry-run 模式，方便在不复制文件的情况下验证解析结果：

```bash
python copy_from_list.py \
  test_workspace/source \
  test_workspace/output_tree_dry_run \
  test_workspace/manifests/tree_manifest.txt \
  --ext pdf --ext docx --dry-run
```

若需使用绝对路径清单，请确保第 2 步已生成最新文件，然后执行：

```bash
python copy_from_list.py \
  test_workspace/source \
  test_workspace/output_absolute_dry_run \
  test_workspace/manifests/absolute_manifest.txt \
  --ext pdf --ext docx --dry-run
```

去掉 `--dry-run` 即可进行真实复制。复制结果会出现在 `test_workspace/output_*` 目录，可直接删除后重复测试。

## 5. 拓展建议

* 将额外的文件类型加入 `--ext` 参数，观察解析匹配情况。
* 在清单中刻意引入不存在的文件，了解缺失项统计输出。
* 修改模板生成器以适配团队共享路径，形成更贴合业务的测试数据集。
