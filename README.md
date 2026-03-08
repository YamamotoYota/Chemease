# Chemease

化学工学エンジニア向けの、日本語 UI で使える Streamlit ベースの化工計算アプリです。化学工学便覧レベルの基礎式・経験式・簡易設計式を、単位換算・物性候補表示・案件保存付きで扱えるようにしています。

## アプリ概要

- 日本語 UI のローカル Web アプリ
- 式の意味、適用条件、前提、注意点を画面表示
- `pint` による標準単位ベースの単位換算
- JSON 管理の式定義・物性 DB
- SQLite 管理の案件保存
- 物性 DB 候補を入力へ反映し、手入力上書きも可能
- 将来の式追加や熱力学モデル追加をしやすい分離構造

初期版では以下の 54 式を搭載しています。

- 流体: 10 式
- 伝熱: 10 式
- 物質移動: 7 式
- 蒸留・分離: 5 式
- 反応工学: 8 式
- 粉体・機械操作: 5 式
- 物性・基礎化工計算: 9 式

## 主な機能

- 計算カテゴリ一覧とキーワード検索
- 各式の説明、LaTeX、適用条件、前提、注意事項の表示
- 入力ごとの単位選択と内部標準単位への換算
- 代表物質 DB からの物性候補読込
- 物性値のセッション内手入力上書き
- 案件作成、案件ごとの計算ケース保存・再読込・複製
- 結果の CSV / JSON 出力
- `pytest` による主要機能テスト

## 画面イメージの説明

### ホーム

- アプリ概要
- カテゴリ別の搭載式数
- 検索ボックス
- よく使う計算
- 最近使った計算
- 案件管理への導線

### 計算

- カテゴリ、式選択、検索
- 計算式名、概要、詳細、LaTeX
- 適用条件、前提、注意事項、変数説明
- 入力値、入力単位、圧力基準
- 物性 DB 候補の表示と反映
- 計算結果、内部換算値、警告、簡単な解釈
- 案件保存、CSV / JSON 出力

### 案件管理

- 案件作成
- 案件一覧
- 保存済みケース一覧
- ケースの詳細確認
- ケース再読込、複製
- ケース比較の基礎表示

### 物性参照

- 物質名検索
- 物性一覧
- 適用温度範囲、出典、注意事項
- セッション内の手入力上書き

## ディレクトリ構成

```text
Chemease/
├─ app.py
├─ requirements.txt
├─ README.md
├─ ui/
│  ├─ home.py
│  ├─ calculator_page.py
│  ├─ project_page.py
│  ├─ property_page.py
│  ├─ info_page.py
│  └─ components.py
├─ calculator_engine/
│  ├─ engine.py
│  ├─ common.py
│  ├─ formulas_fluid.py
│  ├─ formulas_heat.py
│  ├─ formulas_mass_transfer.py
│  ├─ formulas_separation.py
│  ├─ formulas_reaction.py
│  ├─ formulas_particles.py
│  └─ formulas_basic.py
├─ formula_registry/
│  ├─ models.py
│  ├─ loader.py
│  └─ registry.py
├─ unit_conversion/
│  ├─ units.py
│  ├─ custom_units.py
│  └─ converters.py
├─ property_database/
│  ├─ property_models.py
│  ├─ property_loader.py
│  └─ property_service.py
├─ validation/
│  ├─ rules.py
│  └─ validators.py
├─ project_storage/
│  ├─ project_models.py
│  ├─ project_repository.py
│  └─ project_service.py
├─ reporting/
│  ├─ formatters.py
│  └─ exporters.py
├─ data/
│  ├─ formulas/
│  │  ├─ fluid.json
│  │  ├─ heat.json
│  │  ├─ mass_transfer.json
│  │  ├─ separation.json
│  │  ├─ reaction.json
│  │  ├─ particles.json
│  │  └─ basic.json
│  ├─ properties/
│  │  └─ substances.json
│  └─ sample_cases.json
├─ projects/
│  └─ .gitkeep
└─ tests/
   ├─ test_units.py
   ├─ test_registry.py
   ├─ test_properties.py
   ├─ test_project_storage.py
   ├─ test_formulas_fluid.py
   ├─ test_formulas_heat.py
   ├─ test_formulas_basic.py
   ├─ test_formulas_reaction.py
   ├─ test_formulas_particles.py
   └─ test_validation.py
```

## セットアップ方法

### 前提

- Python 3.11 以上
- Windows / macOS / Linux いずれでも可

### インストール

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS / Linux の場合:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 起動方法

```bash
streamlit run app.py
```

初回起動時に以下が利用可能です。

- 54 の計算式
- 10 物質の代表物性 DB
- SQLite ベースの案件保存先

## テスト方法

```bash
python -m pytest -q
```

## 単位換算の考え方

- すべての計算は内部で標準単位へ正規化して実行
- 温度は絶対温度と温度差を分けて扱う
- 圧力は絶対圧 / ゲージ圧を区別
- `Nm^3/h`、`wt%`、`mol%`、`mass_ppm` など実務的な表現に対応
- `kgf/cm^2G` / `kgf/cm^2A` に対応

## 物性 DB 更新方法

物性 DB は `data/properties/substances.json` を編集します。

### 追加・更新手順

1. `substance_id` を一意に決める
2. `name_ja` と `aliases` を設定する
3. 必要な物性項目を `value` と `unit` で追加する
4. `temperature_range`、`notes`、`source` を明記する
5. 必要ならテストを追加する

### 物性 JSON 例

```json
{
  "substance_id": "sample",
  "name_ja": "サンプル物質",
  "aliases": ["Sample"],
  "density": {"value": 1000.0, "unit": "kg/m^3", "note": "代表値"},
  "source": "社内標準物性表"
}
```

## 式追加方法

式追加は、**メタデータ** と **計算ロジック** を分けて行います。

### 1. JSON に式定義を追加

対応カテゴリの JSON ファイルへ新しい式オブジェクトを追加します。

- `data/formulas/fluid.json`
- `data/formulas/heat.json`
- `data/formulas/mass_transfer.json`
- `data/formulas/separation.json`
- `data/formulas/reaction.json`
- `data/formulas/particles.json`
- `data/formulas/basic.json`

最低限、以下を追加します。

- `formula_id`
- `name_ja`
- `category`
- `summary`
- `description`
- `equation_latex`
- `inputs`
- `outputs`
- `variable_definitions`
- `applicability`
- `assumptions`
- `cautions`
- `references`
- `function_name`

### 2. Python 関数を実装

対応カテゴリの `calculator_engine/formulas_*.py` に関数を追加し、`FUNCTIONS` マップへ登録します。

### 3. テストを追加

近いカテゴリの `tests/test_formulas_*.py` にテストを追加します。

## 案件保存の仕様

初期版では SQLite を採用しています。理由は以下です。

- `Project` と `CalculationCase` の関係を保ちやすい
- JSON より一覧・検索・更新がしやすい
- ローカルアプリで配布しやすい
- 将来の比較機能や履歴管理へ拡張しやすい

保存先 DB:

- `projects/chemease.db`

### 保存対象

- `Project`
  - `project_id`
  - `name`
  - `description`
  - `created_at`
  - `updated_at`
- `CalculationCase`
  - `case_id`
  - `project_id`
  - `formula_id`
  - `formula_name`
  - `input_values`
  - `input_units`
  - `pressure_bases`
  - `normalized_inputs`
  - `output_values`
  - `output_units`
  - `warnings`
  - `selected_properties`
  - `overridden_properties`
  - `created_at`
  - `updated_at`

### できること

- 新規案件作成
- 計算結果を案件へ保存
- 保存済みケース読込
- ケース複製
- ケース比較の基礎表示

## サンプルデータ

- 式定義: `data/formulas/*.json`
- 物性 DB: `data/properties/substances.json`
- サンプルケース: `data/sample_cases.json`

## 今後の拡張案

- Antoine 式、蒸気圧 DB、相平衡計算
- 活量係数モデル、EOS ベース熱力学
- さらに多くの相関式・装置設計式追加
- PDF / Excel 帳票出力
- ケース比較の差分表示強化
- 物性 DB のバージョン管理とインポート機能

## ライセンス

このプロジェクトは MIT ライセンスで公開しています。

- ライセンス本文: `LICENSE`
- 著作権者: Yota Yamamoto

## 注意事項

- 初期版は **MVP** として広く浅く式を搭載しています。
- 多くの式は便覧レベルの**簡易式・近似式**です。
- 物性値は**代表値・参考値**です。
- 実機設計、法規対応、最終仕様決定では、必ず対象条件に合う最新データ・詳細設計式をご確認ください。
