# copy_from_list.py
import re
import os
import shutil
import argparse
from pathlib import Path

def compile_file_regex(exts):
    # exts: {"pdf", "docx"} -> .(pdf|docx)$  忽略大小写
    ex_pat = "|".join(sorted(re.escape(e.lstrip(".").lower()) for e in exts))
    # 文件行：前导缩进 + 纯文件名（不能包含 \/:*?"<>|）+ 指定后缀
    return re.compile(
        rf'^(?P<indent>[│\s]*)(?![├└]─)(?P<name>[^\\/:*?"<>|]+\.(?:{ex_pat}))\s*$',
        re.IGNORECASE,
    )

# 目录行：前导缩进 + (├─|└─) + 目录名
DIR_RE = re.compile(r'^(?P<indent>[│\s]*)(?:├─|└─)(?P<name>.+?)\s*$')

def depth_of(indent: str) -> int:
    """
    根据前导缩进判断层级。
    说明：tree 的缩进会混用 '│' 和空格。为了稳妥，这里把竖线和空格都计入宽度，
    再按“每2个字符≈一层”粗略折算。这样即使某些层是空格占位，也不会明显低估层级。
    """
    if not indent:
        return 0
    # 去掉不可见字符，只保留常见空白与竖线
    s = indent.replace("\t", "    ")
    return max(0, len(s) // 2)

def parse_tree_file(tree_file: Path, file_re):
    """
    从 tree /F 的文本输出中解析出【带层级的相对文件路径】。
    关键修复：文件行不再用缩进算层级，而是直接挂到当前目录栈 stack 的最深层。
    """
    files = []
    stack: list[str] = []  # 路径栈，stack[depth] = 该层的目录名

    # 为了兼容 BOM 和本地编码，这里做个小策略
    tried_encodings = ("utf-8-sig", "utf-8", os.device_encoding(1) or "mbcs")
    last_err = None
    for enc in tried_encodings:
        try:
            with tree_file.open(encoding=enc, errors="strict") as f:
                lines = f.readlines()
            break
        except Exception as e:
            last_err = e
    else:
        raise RuntimeError(f"无法解码清单文件：{tree_file}，最后错误：{last_err}")

    for raw in lines:
        s = raw.rstrip("\r\n")
        if not s.strip():
            continue

        # 目录行：更新目录栈
        m_dir = DIR_RE.match(s)
        if m_dir:
            d = depth_of(m_dir.group("indent"))
            name = m_dir.group("name").strip()
            # 将栈截到该深度，然后压入当前目录
            if d <= len(stack):
                stack = stack[:d]
            stack.append(name)
            continue

        # 文件行：直接归属到「当前目录栈」的最深层
        m_file = file_re.match(s)
        if m_file:
            name = m_file.group("name").strip()
            parts = stack + [name]  # 关键修复：不再用缩进 d 推断，直接跟随当前目录栈
            rel_path = Path(*parts)
            files.append(rel_path)
            continue

        # 其他无关行忽略（如最顶上的盘符标题、统计行等）

    return files

def copy_files(rel_paths, src_root: Path, dst_root: Path, dry_run=False):
    copied, missing, skipped = 0, 0, 0
    seen = set()

    for rel in rel_paths:
        # 去掉可能出现的前导/尾随空白
        rel = Path(str(rel).strip())

        # 去重（tree 列表里一般不会重复，但稳妥起见）
        if rel in seen:
            skipped += 1
            continue
        seen.add(rel)

        src = src_root / rel
        dst = dst_root / rel

        if not src.exists():
            print(f"[MISS] {src}")
            missing += 1
            continue

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"[COPY] {src} -> {dst}")
        copied += 1

    print(f"\nDone. Copied: {copied}, Missing: {missing}, Skipped(dup): {skipped}")

def main():
    ap = argparse.ArgumentParser(description="从 tree /F 输出清单按原层级拷贝指定类型文件")
    ap.add_argument("source_root", help="源根目录（生成 tree /F 的那个目录）")
    ap.add_argument("target_root", help="目标根目录（拷贝到这里）")
    ap.add_argument("list_file", help="tree /F 的文本输出文件")
    ap.add_argument(
        "--ext",
        action="append",
        default=["pdf"],
        help="要拷贝的扩展名（不带点），可多次给出，例如 --ext pdf --ext docx；默认 pdf",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="演练模式：只打印将要拷贝的路径，不实际复制",
    )
    args = ap.parse_args()

    src = Path(args.source_root)
    dst = Path(args.target_root)
    lst = Path(args.list_file)

    if not src.exists():
        raise SystemExit(f"源目录不存在：{src}")
    if not lst.exists():
        raise SystemExit(f"清单文件不存在：{lst}")

    file_re = compile_file_regex(set(args.ext))
    rel_paths = parse_tree_file(lst, file_re)

    if not rel_paths:
        print("清单里没有匹配到文件（请检查扩展名/正则是否正确，或确认清单是 tree /F 的输出）")
        return

    copy_files(rel_paths, src, dst, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
