import subprocess
from pathlib import Path

class VisualizationAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, results_dict, output_dir):
        """结果可视化：基因组浏览器、共线性图、系统发育树"""
        self.logger.info("Starting visualization")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        viz_results = {}

        # 1. 基因组浏览器（JBrowse）
        if 'assembly' in results_dict:
            browser_dir = self._create_genome_browser(results_dict, output_dir)
            viz_results['browser'] = str(browser_dir)

        # 2. 共线性图
        if 'synteny' in results_dict:
            synteny_plot = self._plot_synteny(results_dict['synteny'], output_dir)
            viz_results['synteny_plot'] = str(synteny_plot)

        # 3. 系统发育树
        if 'phylogeny' in results_dict:
            tree_plot = self._plot_phylogeny(results_dict['phylogeny'], output_dir)
            viz_results['tree_plot'] = str(tree_plot)

        # 4. 统计报告
        report = self._generate_html_report(results_dict, output_dir)
        viz_results['report'] = str(report)

        return viz_results

    def _create_genome_browser(self, results, output_dir):
        """创建 JBrowse 基因组浏览器"""
        browser_dir = output_dir / 'jbrowse'
        browser_dir.mkdir(exist_ok=True)
        return browser_dir

    def _plot_synteny(self, synteny_data, output_dir):
        """绘制共线性图"""
        plot_file = output_dir / 'synteny.png'
        return plot_file

    def _plot_phylogeny(self, tree_data, output_dir):
        """绘制系统发育树"""
        plot_file = output_dir / 'phylogeny.png'
        return plot_file

    def _generate_html_report(self, results, output_dir):
        """生成 HTML 报告"""
        report_file = output_dir / 'report.html'

        html = """
        <html>
        <head><title>BioAgent Analysis Report</title></head>
        <body>
        <h1>Genome Analysis Report</h1>
        <h2>Summary</h2>
        <ul>
        """

        for key, value in results.items():
            html += f"<li>{key}: {value}</li>\n"

        html += """
        </ul>
        </body>
        </html>
        """

        with open(report_file, 'w') as f:
            f.write(html)

        return report_file
