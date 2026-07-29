#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jmle-charcount — 医師国家試験問題の文字数に関する定量的分析(第101〜120回)で用いた計数規則の
                 リファレンス実装(単体版・依存なし)。

本研究の主指標 "body" = ひらがな・カタカナ・漢字・英字(ギリシャ含)・数字を 1字＝1カウント
                        (句読点・記号・スペースを除外)= 学会抄録と同一の定義。
副指標 "総印字文字数" = 句読点・記号も含む(スペースのみ除外)。

前処理: Unicode NFC 正規化 → 制御/書式文字(Cc/Cf)を除去 → 空白を除外。

使い方:
    python count.py "テキスト"
    cat file.txt | python count.py
    python count.py --self-test
"""
from __future__ import annotations
import sys
import re
import json
import unicodedata
from collections import defaultdict

BODY_CLASSES = ("kanji", "hiragana", "katakana", "latin", "digit")
_CTRL_CAT = ("Cc", "Cf")


def char_class(ch: str) -> str:
    """1文字を8クラスのいずれかに分類する(研究本体 charcount/count.py と同一定義)。"""
    o = ord(ch)
    if ch in " 　\t\n\r\f\v":
        return "whitespace"
    if 0x3040 <= o <= 0x309F:
        return "hiragana"
    if 0x30A0 <= o <= 0x30FF or 0x31F0 <= o <= 0x31FF:
        return "katakana"
    if (0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF
            or 0xF900 <= o <= 0xFAFF or 0x20000 <= o <= 0x2FA1F or ch in "々〆〤ヶ"):
        return "kanji"
    if (0x41 <= o <= 0x5A or 0x61 <= o <= 0x7A                 # ASCII Latin
            or 0xFF21 <= o <= 0xFF3A or 0xFF41 <= o <= 0xFF5A  # 全角 Latin
            or 0xC0 <= o <= 0x24F                              # 拡張 Latin
            or ch in "αβγδεζηθικλμνξοπρστυφχψω"):              # ギリシャ小文字
        return "latin"
    if ch.isdigit() or 0xFF10 <= o <= 0xFF19:
        return "digit"
    cat = unicodedata.category(ch)
    if cat.startswith("P") or ch in "、。「」『』〈〉《》【】・…―":
        return "punct"
    if cat.startswith("S") or ch in "℃％±×÷≦≧〒":
        return "symbol"
    return "other"


def count_text(text: str) -> dict:
    """テキスト1件の計数結果を返す。"""
    nfc = unicodedata.normalize("NFC", text or "")
    nfc = "".join(ch for ch in nfc if unicodedata.category(ch) not in _CTRL_CAT)
    no_ws = re.sub(r"\s+", "", nfc)

    by_class: dict[str, int] = defaultdict(int)
    for ch in nfc:
        by_class[char_class(ch)] += 1

    body = sum(by_class.get(c, 0) for c in BODY_CLASSES)
    return {
        "body": body,                                  # ★主指標
        "printed_total": len(no_ws),                   # 副指標: 句読点・記号込み(空白除外)
        "with_whitespace": len(nfc),                   # 参考: 空白込み
        "by_class": {k: by_class[k] for k in sorted(by_class)},
        "kanji_pct": round(by_class.get("kanji", 0) / body * 100, 1) if body else 0.0,
        "latin_pct": round(by_class.get("latin", 0) / body * 100, 1) if body else 0.0,
    }


def _self_test() -> int:
    cases = [
        # 患者(2)は(1)72(2)歳(1)の(1)男性(2)=body 9 / 「。」を足して副指標 10
        ("患者は72歳の男性。", {"body": 9, "printed_total": 10}),
        ("HbA1c 7.2%(基準 4.6〜6.2)", {"body": 13, "printed_total": 20}),
        ("", {"body": 0, "printed_total": 0}),
    ]
    ok = True
    for text, exp in cases:
        got = count_text(text)
        if exp:
            for k, v in exp.items():
                if got[k] != v:
                    print(f"FAIL {text!r} {k}: {got[k]} != {v}")
                    ok = False
        print(f"  {text!r:40} body={got['body']:4d} printed={got['printed_total']:4d} {got['by_class']}")
    print("self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return _self_test()
    text = " ".join(args) if args else sys.stdin.read()
    print(json.dumps(count_text(text), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
