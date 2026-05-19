# claude-config

Claude Code のグローバル設定を管理する dotfiles リポジトリ。

新しいマシンで `setup.sh` を実行するだけで、AI エージェントが自走して開発を完成させるための共通基盤が整います。

## 設計方針

**グローバル設定（このリポジトリ）** と **プロジェクト設定（`.claude/`）** で役割を分離しています。

| 層 | 場所 | 内容 |
|---|---|---|
| グローバル | `~/.claude/`（このリポジトリ） | git・gh 操作、品質ガード、汎用エージェント |
| プロジェクト | `プロジェクトルート/.claude/` | スタック固有コマンド、ドメイン知識、CI設定 |

プロジェクト側は `/init-autonomous` を実行すると自動生成されます。

## 含まれるもの

| ディレクトリ/ファイル | 内容 |
|---|---|
| `agents/` | 9体のカスタムエージェント（planner, tdd-guide, code-reviewer, security-reviewer など） |
| `commands/` | スラッシュコマンド（/design, /plan, /tdd, /commit, /create-pr, /init-autonomous など） |
| `hooks/` | 品質ガードフック（console.log 警告・シークレット検出・セッション終了監査） |
| `rules/` | コーディングスタイル、テスト要件、セキュリティ、エージェント運用ガイドライン |
| `skills/` | 参照ドキュメント（フロントエンド/バックエンドパターン、git-workflow など） |
| `settings.json.template` | Claude Code 設定テンプレート（インストール時にパス自動解決） |

## settings.json.template の主な設定

- `defaultMode: auto` — ほとんどの操作を自動承認
- `Bash(git *)` / `Bash(gh *)` — どのプロジェクトでも git/gh 操作が確認なしで動作
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: 1` — 複数エージェントの並列実行を有効化
- フック: Stop 時に音声通知（macOS: afplay / Linux: terminal bell）+ console.log 監査

## 新しいマシンへのインストール

```bash
git clone https://github.com/ShigetomoYamamoto/claude-config.git ~/dotfiles/claude-config
cd ~/dotfiles/claude-config
./setup.sh
```

`setup.sh` は以下を行います：
- `agents/`, `commands/`, `hooks/`, `rules/`, `skills/` を `~/.claude/` にコピー
- `settings.json.template` からパスを解決して `~/.claude/settings.json` を生成

## 使い方

### パターン1: 既存プロジェクトへの導入

仕様書・設計書など必要な資料が揃っている前提です。

```
# ステップ1: AI エージェント自走基盤を生成
/init-autonomous
```

スタックを自動検出し、以下を一括生成します：
- `.claude/settings.json` — スタック固有コマンドの権限設定（npm/pest/pytest/go/cargo など）
- `CLAUDE.md` — プロジェクトルール・エンティティ・ロール定義
- `.claude/rules/`, `.claude/commands/`, `.claude/agents/` — スタック固有の設定
- `docs/` — 仕様書テンプレート・ADR・コードマップ
- `.github/` — CI/CD・PRテンプレート・Issue テンプレート

**ステップ2: 既存資料を Claude に読み込ませる**

2つの方法があります：

- **生成されたテンプレートを使う場合**: `docs/01_product-specifications.md`・`docs/02_detailed-design.md` に既存資料の内容を記入する
- **既存ファイルをそのまま使う場合**: 生成された `CLAUDE.md` の参照パスを既存ファイルのパスに書き換える

ここまで完了すると、Claude が仕様・設計・コードベースを把握した状態になります。以降は通常の開発フローで進めます。

```
# 通常の開発フロー
/plan      → /tdd      → /commit    → /create-pr
（実装計画）  （TDD実装）  （レビュー→コミット）  （レビュー→PR）
```

---

### パターン2: 新規プロジェクト作成直後

コードも資料もほぼない状態から始めます。まず要件定義・設計を行い、その成果物を使って自走基盤を構築します。

```
# ステップ1: 要件定義・システム設計
/design
```

機能要件・非機能要件・データモデル・APIコントラクトを定義します。承認するまで実装には進みません。

```
# ステップ2: AI エージェント自走基盤を生成
/init-autonomous
```

```
# ステップ3: 設計内容を docs/ に反映
docs/01_product-specifications.md  ← /design の要件定義を記入
docs/02_detailed-design.md         ← /design の詳細設計を記入
```

```
# ステップ4: 実装開始
/plan      → /tdd      → /commit    → /create-pr
```

---

## 別マシンで最新の設定を取得するとき

```bash
cd ~/dotfiles/claude-config
git pull
./setup.sh
```

## プラグイン（別マシンで手動インストールが必要）

設定ファイルに有効化フラグは含まれていますが、プラグイン本体は別途インストールが必要です：

```bash
claude plugin install slack
claude plugin install supabase
claude plugin install vercel
```
