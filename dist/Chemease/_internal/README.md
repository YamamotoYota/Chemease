# Chemease

化学工学エンジニア向けの、日本語 UI で使える Streamlit ベースの化工計算アプリです。化学工学便覧レベルの基礎式・経験式・簡易設計式を、単位換算、物性 DB、案件保存、GUI 編集付きで扱えるようにしています。

## アプリ概要

- 日本語 UI のローカル Web アプリ
- 式の意味、適用条件、前提、注意点を画面表示
- `pint` による標準単位ベースの単位換算
- JSON 管理の式定義と基礎物性 DB
- SQLite 管理の案件保存
- 物性 DB を GUI 上で登録、編集、削除可能
- ユーザー定義式を GUI から登録、編集、削除可能
- 単一出力の式では入力変数の逆算に対応
- 将来の式追加や熱力学モデル追加をしやすい分離構造

現行版では以下の 210 式を搭載しています。

- 流体: 32 式
- 伝熱: 32 式
- 物質移動: 29 式
- 蒸留・分離: 28 式
- 反応工学: 31 式
- 粉体・機械操作: 27 式
- 物性・基礎化工計算: 31 式

物性 DB は 471 物質を収録し、代表値に加えて沸点、融点、臨界物性、蒸発潜熱、粘度などを保持できます。主要物質は既存の代表値を維持しつつ、`Property.xlsx` 由来の値で更新しています。

## 主な機能

- 計算カテゴリ一覧とキーワード検索
- 各式の説明、LaTeX、適用条件、前提、注意事項の表示
- 入力ごとの単位選択と内部標準単位への換算
- 代表物質 DB からの物性候補読込
- 物性 DB の GUI 登録、編集、削除
- ユーザー定義式の GUI 登録、編集、削除
- 計算時の案件内一時上書き
- 単一出力式に対する任意変数の逆算
- 案件作成、案件ごとの計算ケース保存、再読込、複製
- 結果の CSV / JSON 出力
- `pytest` による主要機能テスト
- Windows 向け実行ファイルのビルド対応

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
- 通常計算 / 任意変数逆算の切替
- 適用条件、前提、注意事項、変数説明
- 入力値、入力単位、圧力基準
- 物性 DB 候補の表示と反映
- 計算結果、内部換算値、警告、簡単な解釈
- 案件保存、CSV / JSON 出力

### 式管理

- ユーザー定義式の新規登録
- 既存ユーザー式の編集、削除
- expression ベースの単一出力式登録
- 登録後すぐに計算画面へ反映

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
- 案件内の一時上書き
- GUI からの新規登録、既存編集、削除

## ディレクトリ構成

```text
Chemease/
├─ app.py
├─ launcher.py
├─ requirements.txt
├─ requirements-build.txt
├─ README.md
├─ LICENSE
├─ Chemease.spec
├─ build_exe.ps1
├─ scripts/
│  └─ import_property_excel.py
├─ ui/
│  ├─ home.py
│  ├─ calculator_page.py
│  ├─ formula_page.py
│  ├─ project_page.py
│  ├─ property_page.py
│  ├─ info_page.py
│  └─ components.py
├─ calculator_engine/
│  ├─ engine.py
│  ├─ common.py
│  ├─ expression_evaluator.py
│  ├─ formulas_fluid.py
│  ├─ formulas_heat.py
│  ├─ formulas_mass_transfer.py
│  ├─ formulas_separation.py
│  ├─ formulas_reaction.py
│  ├─ formulas_particles.py
│  └─ formulas_basic.py
├─ formula_registry/
│  ├─ custom_formula_repository.py
│  ├─ custom_formula_service.py
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
│  ├─ property_repository.py
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
│  │  ├─ fluid_handbook.json
│  │  ├─ heat.json
│  │  ├─ heat_handbook.json
│  │  ├─ mass_transfer.json
│  │  ├─ mass_transfer_handbook.json
│  │  ├─ separation.json
│  │  ├─ separation_handbook.json
│  │  ├─ reaction.json
│  │  ├─ reaction_handbook.json
│  │  ├─ particles.json
│  │  ├─ particles_handbook.json
│  │  ├─ basic.json
│  │  └─ basic_handbook.json
│  ├─ properties/
│  │  └─ substances.json
│  └─ sample_cases.json
├─ projects/
│  ├─ .gitkeep
│  ├─ custom_formulas.json
│  └─ custom_properties.json
└─ tests/
   ├─ test_units.py
   ├─ test_custom_formula_features.py
   ├─ test_registry.py
   ├─ test_properties.py
   ├─ test_packaging_files.py
   ├─ test_project_storage.py
   ├─ test_formulas_fluid.py
   ├─ test_formulas_heat.py
   ├─ test_formulas_basic.py
   ├─ test_formulas_reaction.py
   ├─ test_formulas_particles.py
   ├─ test_formula_handbook_catalog.py
   ├─ test_formulas_extended.py
   └─ test_validation.py
```

## セットアップ方法

### 前提

- Windows
- Miniforge
- `chemease` という conda 仮想環境

### インストール

Miniforge で仮想環境を作る前提です。

```powershell
conda create -n chemease python=3.11
conda activate chemease
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 起動方法

### 開発時

```powershell
conda activate chemease
streamlit run app.py
```

初回起動時に以下が利用可能です。

- 210 の計算式
- 471 物質の物性 DB
- SQLite ベースの案件保存先
- GUI 編集可能なカスタム物性 DB
- GUI 編集可能なカスタム式 DB
- 単一出力式の逆算モード

### 実行ファイル

ローカルビルド済みの Windows 実行ファイルは以下に出力されます。

- `dist/Chemease/Chemease.exe`

実行ファイルを再生成する場合:

```powershell
conda activate chemease
./build_exe.ps1
```

または手動で:

```powershell
conda activate chemease
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt
python -m PyInstaller --noconfirm --clean Chemease.spec
```

`build_exe.ps1` はスクリプト自身の配置場所を起点に動作するため、PowerShell の現在ディレクトリがリポジトリ直下でなくても実行できます。`launcher.py` が Streamlit サーバを起動し、ブラウザで `http://127.0.0.1:8501` を開きます。

## テスト方法

```powershell
conda activate chemease
python -m pytest -q
```

## 単位換算の考え方

- すべての計算は内部で標準単位へ正規化して実行
- 温度は絶対温度と温度差を分けて扱う
- 圧力は絶対圧 / ゲージ圧を区別
- `Nm^3/h`、`wt%`、`mol%`、`mass_ppm` など実務的な表現に対応
- `kgf/cm^2G` / `kgf/cm^2A` に対応

## 物性 DB 更新方法

物性 DB は、同梱 DB とユーザー編集 DB の 2 層構造です。

- 同梱 DB: `data/properties/substances.json`
- ユーザー編集 DB: `projects/custom_properties.json`

同梱 DB の大部分は、`Property.xlsx` をもとに整形しています。

### GUI から追加、編集、削除する

1. アプリの `物性参照` 画面を開く
2. `DB登録・編集` タブを選ぶ
3. `新規登録` または `既存編集` を選ぶ
4. 物質名、別名、物性値、単位、出典、備考を入力する
5. `DBへ保存` を押す
6. ユーザー登録レコードは `projects/custom_properties.json` に保存される

同じ `substance_id` を保存した場合、同梱 DB よりカスタム DB の値が優先されます。

### ファイルを直接更新する

1. `substance_id` を一意に決める
2. `name_ja` と `aliases` を設定する
3. 必要な物性項目を `value` と `unit` で追加する
4. 必要に応じて `note`、`temperature_range`、`source`、`phase_reference` を記載する
5. 反映後にテストを実行する

### Excel から再生成する

`Property.xlsx` のような便覧 Excel から同梱 DB を再生成する場合:

```powershell
conda activate chemease
python scripts/import_property_excel.py --excel "C:\path\to\Property.xlsx"
```

- 入力 Excel: `--excel`
- 出力 JSON: 省略時は `data/properties/substances.json`
- 既存の代表物性は保持しつつ、分子量、融点、沸点、臨界物性、粘度、蒸発潜熱などを上書き、補完します
- 同分子式の異性体は別レコードとして保持します

### 物性 JSON 例

```json
{
  "substance_id": "sample",
  "name_ja": "サンプル物質",
  "aliases": ["Sample"],
  "density": {"value": 1000.0, "unit": "kg/m^3", "note": "代表値"},
  "boiling_point": {"value": 373.15, "unit": "K", "note": "1 atm"},
  "source": "社内標準物性表"
}
```

## 式追加方法

式追加には、GUI 登録とコード追加の 2 通りがあります。

### GUI から追加する

1. アプリの `式管理` を開く
2. `新規登録` を選ぶ
3. 式名、カテゴリ、LaTeX、expression を入力する
4. 入力変数と出力変数のキー、単位、制約を設定する
5. `式を保存` を押す
6. 保存先は `projects/custom_formulas.json`

現在の GUI 登録式は、単一出力の expression ベース式に対応しています。expression には入力変数キーのみを使います。

例:

```text
density * velocity * diameter / viscosity
```

### コードで追加する

式追加は、メタデータと計算ロジックを分けて行います。

### 1. JSON に式定義を追加

対応カテゴリの JSON ファイルへ新しい式オブジェクトを追加します。

- `data/formulas/fluid.json`
- `data/formulas/heat.json`
- `data/formulas/mass_transfer.json`
- `data/formulas/separation.json`
- `data/formulas/reaction.json`
- `data/formulas/particles.json`
- `data/formulas/basic.json`
- `projects/custom_formulas.json`（GUI 管理式）

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
- JSON より一覧、検索、更新がしやすい
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
  - `calculation_mode`
  - `input_values`
  - `input_units`
  - `pressure_bases`
  - `normalized_inputs`
  - `output_values`
  - `output_units`
  - `solve_metadata`
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
- ユーザー式 DB: `projects/custom_formulas.json`
- 物性 DB: `data/properties/substances.json`
- ユーザー物性 DB: `projects/custom_properties.json`
- Excel 取込スクリプト: `scripts/import_property_excel.py`
- サンプルケース: `data/sample_cases.json`

## 今後の拡張案

- Antoine 式、蒸気圧 DB、相平衡計算
- 活量係数モデル、EOS ベース熱力学
- 装置設計式、配管設計式、伝熱相関式の追加
- PDF / Excel 帳票出力
- ケース比較の差分表示強化
- 物性 DB のインポート、エクスポート、承認フロー

## ライセンス

このプロジェクトは MIT ライセンスで公開しています。

- ライセンス本文: `LICENSE`
- 著作権者: Yota Yamamoto

## 注意事項

- 多くの式は便覧レベルの簡易式、近似式です。
- 物性値は代表値、参考値です。
- GUI で編集した物性 DB はローカルの `projects/custom_properties.json` に保存されます。
- 実機設計、法規対応、最終仕様決定では、必ず対象条件に合う最新データ、詳細設計式、実測値をご確認ください。
