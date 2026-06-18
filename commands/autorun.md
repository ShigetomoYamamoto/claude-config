---
name: 自走モード
description: |
  完了条件を渡すと、ハードストップを設定した上で達成まで自律的に作業を継続します。
  /goal・/loop・ScheduleWakeup・CronCreate・Workflow を状況に応じて使い分けます。
---

# /autorun — 自走モード（ハードストップ付き）

完了条件を1つ渡すと、`rules/loop-safety.md` の安全条件を満たした上で、その条件を満たすまで人間のプロンプトなしで作業を継続する。

**このコマンドの原則:** ブレーキのないループは事故。走り出す前に `rules/loop-safety.md` の前提を満たし、ハードストップを設定する。

## ステップ 1: 前提を満たす

`rules/loop-safety.md` の **Preconditions**（完了条件が一文で言え機械検証できる / 専用ブランチ・worktree / 機械的な成功テスト / ハードストップ）をすべて満たすか確認する。1つでも欠ければ自走を始めず、不足を報告して止まる。ハードストップ未指定時の既定値（20ターン or 30分）も loop-safety.md に従う。

## ステップ 2: 手段の選択

完了条件と起動契機に応じて使い分ける:

| 状況 | 使う仕組み |
|------|-----------|
| 単一の完了条件まで自走（テストが通るまで等） | 組み込み `/goal <条件> or stop after <N> turns` |
| 一定間隔で繰り返し起動（CI 監視・PR 巡回等） | `/loop <interval> <command>` または `ScheduleWakeup` |
| 決まった時刻・cron で起動 | `CronCreate`（schedule スキル） |
| 多数の独立タスクをファンアウトして検証 | `Workflow`（pipeline / parallel） |

## ステップ 3: 自走

1. **完了条件の定式化** — 機械検証可能な形に落とす。Claude 自身の出力で証明できる条件にする。
2. **開始** — ステップ 2 で選んだ手段で走らせる。
3. **反復中の規律は `rules/loop-safety.md` に従う** — 特に Goal drift（条件からズレたら新目標を作らず STOP）と Irreversible / outward-facing actions（push / deploy / delete / 外部送信の前で人間に確認）。

## ステップ 4: 停止と報告

完了条件の達成、またはハードストップ到達で停止し、達成 / 未達・消費したターン数・時間（・概算トークン）・残課題を報告する。

## 関連

- `rules/loop-safety.md` — 安全運用の規範（前提条件・ハードストップ・ゴールドリフト・不可逆操作の唯一の正）
- `rules/agents.md` — エージェント自動起動のトリガー表
