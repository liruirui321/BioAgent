# Genome Assembly Multi-Agent System

基因组组装与注释的 Multi-Agent 自动化系统，支持质控驱动的回溯机制。

## 功能特性

- **自动化流程**: 组装 → 重复注释 → 结构注释 → 功能注释
- **质控检查**: 每步自动运行 BUSCO/QUAST 质控
- **审计日志**: 完整记录所有操作和质控结果
- **物种支持**: 植物/动物/真菌

## 安装

### 依赖工具

需要预先安装以下生物信息学工具：

```bash
# 组装工具
hifiasm
quast
busco

# 重复注释
RepeatModeler
RepeatMasker

# 结构注释
braker3

# 功能注释
eggNOG-mapper
```

### Python 依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python main.py \
  --input reads.hifi.fq.gz \
  --species plant \
  --output results/
```

### 完整参数

```bash
python main.py \
  --input reads.hifi.fq.gz \
  --hic-r1 hic_R1.fq.gz \
  --hic-r2 hic_R2.fq.gz \
  --rnaseq rnaseq.bam \
  --species plant \
  --ploidy 2 \
  --heterozygosity high \
  --output results/ \
  --threads 32
```

## 输出结构

```
results/
├── assembly/          # 组装结果
│   ├── assembly.fasta
│   ├── quast/
│   └── busco/
├── repeat/            # 重复注释
│   ├── assembly.masked.fasta
│   └── repeat_db-families.fa
├── structural/        # 结构注释
│   ├── braker.gff3
│   ├── braker.aa
│   └── busco/
├── functional/        # 功能注释
│   └── annotation.emapper.annotations
└── audit.log          # 审计日志
```

## 质控阈值

配置文件: `config/qc_thresholds.yaml`

- Assembly: BUSCO ≥ 90%, N50 ≥ 1Mb
- Repeat: 重复含量在预期值 50%-150%
- Structural: BUSCO ≥ 85%
- Functional: 注释覆盖率 ≥ 60%

## 回溯机制

系统支持基于质控指标的自动回溯：

**触发条件**：
- 结构注释 BUSCO < 组装 BUSCO - 5% → 回溯到组装
- 单外显子基因比例 > 30% 且重复含量 < 20% → 回溯到重复注释

**限制**：最多回溯 2 次，避免无限循环

## 开发路线图

- [x] Phase 1: MVP - 线性执行流程
- [x] Phase 2: 回溯机制
- [ ] Phase 3: 工具选择器

## License

MIT
