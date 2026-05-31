"""
项目风险早期预警 - 报告生成
生成可视化的风险预警报告
"""

import json
from datetime import datetime
from pathlib import Path

import yaml


class RiskReporter:
    """风险报告生成器"""

    def __init__(self, config_path: str, analysis_results: dict):
        """
        初始化报告生成器

        Args:
            config_path: 配置文件路径
            analysis_results: 分析结果
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.results = analysis_results
        self.report_config = self.config.get('report', {})
        self.risk_levels = self.config.get('risk_levels', {})

    def generate(self) -> dict:
        """生成报告"""
        output_dir = Path(self.report_config.get('output_dir', './reports'))
        output_dir.mkdir(exist_ok=True, parents=True)

        outputs = {}

        formats = self.report_config.get('formats', ['json', 'html'])

        if 'json' in formats:
            outputs['json'] = self.generate_json(output_dir / 'risk_report.json')

        if 'html' in formats:
            outputs['html'] = self.generate_html(output_dir / 'risk_report.html')

        return outputs

    def generate_json(self, output_path: Path) -> str:
        """生成JSON报告"""
        report = {
            'report_info': {
                'title': '项目风险预警报告',
                'generated_at': datetime.now().isoformat(),
                'project': self.results.get('project', '未命名')
            },
            'risk_summary': {
                'overall_score': self.results.get('overall_risk_score', 0),
                'risk_level': self.results.get('risk_level', 'low'),
                'total_risks': len(self.results.get('sorted_risks', [])),
                'priority_risks': [
                    r for r in self.results.get('sorted_risks', [])
                    if r['level'] in ('high', 'critical')
                ]
            },
            'risk_details': self.results.get('risk_probabilities', {}),
            'sorted_risks': self.results.get('sorted_risks', []),
            'top_risk': self.results.get('top_risk', None)
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"JSON报告已生成: {output_path}")
        return str(output_path)

    def generate_html(self, output_path: Path) -> str:
        """生成HTML可视化报告"""
        level_info = self.risk_levels.get(self.results.get('risk_level', 'low'), {})
        level_color = level_info.get('color', 'green')

        risk_rows = ''
        for risk in self.results.get('sorted_risks', []):
            level_name = risk.get('level', 'low')
            level_cfg = self.risk_levels.get(level_name, {})
            color = level_cfg.get('color', 'gray')
            label = level_cfg.get('name', risk['level'])
            prob_pct = risk.get('probability', 0) * 100

            risk_rows += f"""
            <tr class="border-t hover:bg-gray-50">
                <td class="p-3">{risk['name']}</td>
                <td class="p-3">{prob_pct:.1f}%</td>
                <td class="p-3">{risk['risk_score']:.2f}</td>
                <td class="p-3">
                    <span class="px-2 py-1 rounded text-white text-xs" style="background:{color}">{label}</span>
                </td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目风险预警报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-5xl mx-auto">
        <h1 class="text-2xl font-bold mb-2">项目风险预警报告</h1>
        <p class="text-gray-500 mb-6">
            项目: {self.results.get('project', '未命名')} |
            生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>

        <div class="grid grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-lg shadow p-4 text-center">
                <div class="text-2xl font-bold" style="color:{level_color}">
                    {self.results.get('overall_risk_score', 0):.3f}
                </div>
                <div class="text-sm text-gray-500">综合风险评分</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4 text-center">
                <div class="text-2xl font-bold" style="color:{level_color}">
                    {level_info.get('name', '未知')}
                </div>
                <div class="text-sm text-gray-500">风险等级</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4 text-center">
                <div class="text-2xl font-bold text-blue-600">
                    {len(self.results.get('sorted_risks', []))}
                </div>
                <div class="text-sm text-gray-500">风险项数</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4 text-center">
                <div class="text-2xl font-bold text-red-600">
                    {len([r for r in self.results.get('sorted_risks', []) if r['level'] in ('high', 'critical')])}
                </div>
                <div class="text-sm text-gray-500">高优先级</div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow overflow-hidden mb-8">
            <div class="p-4 border-b bg-gray-50 font-bold">风险详情</div>
            <table class="w-full text-sm">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="p-3 text-left">风险名称</th>
                        <th class="p-3 text-left">发生概率</th>
                        <th class="p-3 text-left">风险分数</th>
                        <th class="p-3 text-left">等级</th>
                    </tr>
                </thead>
                <tbody>
                    {risk_rows}
                </tbody>
            </table>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-bold mb-4">应对建议</h2>
            <ul class="space-y-2 text-sm">
                <li class="flex items-start">
                    <span class="text-yellow-500 mr-2">!</span>
                    建议每24小时更新一次风险检测
                </li>
                <li class="flex items-start">
                    <span class="text-yellow-500 mr-2">!</span>
                    对高优先级风险制定专项应对计划
                </li>
                <li class="flex items-start">
                    <span class="text-green-500 mr-2">+</span>
                    建立风险预警通知机制
                </li>
            </ul>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"HTML报告已生成: {output_path}")
        return str(output_path)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    from risk_detector import RiskDetector
    from analyzer import RiskAnalyzer

    detector = RiskDetector('config.yaml')
    signals = detector.detect_all()

    analyzer = RiskAnalyzer('config.yaml')
    results = analyzer.calculate(signals)

    reporter = RiskReporter('config.yaml', results)
    outputs = reporter.generate()

    print(f"\n所有报告已生成完毕")