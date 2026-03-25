#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(14, 16))
ax.set_xlim(0, 10)
ax.set_ylim(0, 20)
ax.axis('off')

# 标题
ax.text(5, 19, 'BioAgent 系统架构', fontsize=20, ha='center', weight='bold')

# 用户输入
input_box = FancyBboxPatch((1, 17.5), 8, 1, boxstyle="round,pad=0.1",
                           edgecolor='blue', facecolor='lightblue', linewidth=2)
ax.add_patch(input_box)
ax.text(5, 18, 'HiFi reads + RNA-seq + 物种类型', ha='center', va='center', fontsize=10)

# Orchestrator
orch_box = FancyBboxPatch((1, 15.5), 8, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='green', facecolor='lightgreen', linewidth=2)
ax.add_patch(orch_box)
ax.text(5, 16.5, 'Orchestrator', ha='center', weight='bold', fontsize=11)
ax.text(5, 16.1, '工具选择 | 回溯引擎 | 质控检查 | LLM辅助', ha='center', fontsize=8)

# Agent 1-3
agents_y = 13.5
for i, (name, tools) in enumerate([
    ('Assembly', 'hifiasm\nQUAST\nBUSCO'),
    ('Repeat', 'RepeatModeler\nRepeatMasker'),
    ('Structural', 'BRAKER3\nBUSCO')
]):
    x = 0.5 + i * 3
    box = FancyBboxPatch((x, agents_y), 2.5, 1.5, boxstyle="round,pad=0.05",
                         edgecolor='orange', facecolor='lightyellow', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x+1.25, agents_y+1.1, f'Agent {i+1}', ha='center', weight='bold', fontsize=9)
    ax.text(x+1.25, agents_y+0.8, name, ha='center', fontsize=9)
    ax.text(x+1.25, agents_y+0.3, tools, ha='center', fontsize=7)

# 回溯检查
back_box = FancyBboxPatch((3, 11.5), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='red', facecolor='#ffcccc', linewidth=2)
ax.add_patch(back_box)
ax.text(5, 12, '回溯检查', ha='center', weight='bold', fontsize=10)

# Agent 4-5
for i, (name, tools) in enumerate([
    ('Functional', 'eggNOG\nInterPro'),
    ('Comparative', 'OrthoFinder\nMCScanX\nPan-genome')
]):
    y = 9.5 - i * 2.5
    box = FancyBboxPatch((1.5, y), 7, 1.5, boxstyle="round,pad=0.05",
                         edgecolor='purple', facecolor='#e6ccff', linewidth=1.5)
    ax.add_patch(box)
    ax.text(5, y+1.1, f'Agent {i+4}', ha='center', weight='bold', fontsize=9)
    ax.text(5, y+0.8, name, ha='center', fontsize=9)
    ax.text(5, y+0.3, tools, ha='center', fontsize=7)

# 新增 Agents (6-10)
new_agents_y = 4.5
for i, (name, desc) in enumerate([
    ('Karyotype', '核型/倍性'),
    ('Phylogeny', '系统发育'),
    ('TE', '转座子'),
    ('Metabolite', '代谢物'),
    ('Visualization', '可视化')
]):
    x = 0.2 + i * 2
    box = FancyBboxPatch((x, new_agents_y), 1.8, 1, boxstyle="round,pad=0.05",
                         edgecolor='teal', facecolor='#ccffff', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x+0.9, new_agents_y+0.7, f'Agent {i+6}', ha='center', weight='bold', fontsize=8)
    ax.text(x+0.9, new_agents_y+0.3, name, ha='center', fontsize=7)
    ax.text(x+0.9, new_agents_y+0.05, desc, ha='center', fontsize=6)

# 输出
output_box = FancyBboxPatch((2, 2), 6, 1.5, boxstyle="round,pad=0.1",
                            edgecolor='darkgreen', facecolor='#ccffcc', linewidth=2)
ax.add_patch(output_box)
ax.text(5, 3.2, '输出结果', ha='center', weight='bold', fontsize=11)
ax.text(5, 2.7, '组装序列 | 基因注释 | 功能注释', ha='center', fontsize=8)
ax.text(5, 2.4, '比较基因组 | 质控报告 | 审计日志', ha='center', fontsize=8)

# 箭头
arrows = [
    (5, 17.5, 5, 17), (5, 15.5, 5, 15), (5, 13.5, 5, 12.5),
    (5, 11.5, 5, 11), (5, 9.5, 5, 7), (5, 5.5, 5, 3.5)
]
for x1, y1, x2, y2 in arrows:
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->',
                           mutation_scale=20, linewidth=2, color='black')
    ax.add_patch(arrow)

# 图例
legend_y = 0.5
ax.text(1, legend_y, '✅ 已实现 (5个)', fontsize=9, color='orange', weight='bold')
ax.text(5, legend_y, '⭕ 新增 (5个)', fontsize=9, color='teal', weight='bold')

plt.tight_layout()
plt.savefig('/data/work/analysis/project/genome-assembly-agents/architecture.png',
            dpi=300, bbox_inches='tight')
print("流程图已保存: architecture.png")
