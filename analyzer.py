"""
项目风险早期预警 - 概率计算
计算各类风险的发生概率和影响
"""

import json
import math
from datetime import datetime
from pathlib import Path

import yaml


class RiskAnalyzer:
    """风险概率分析器"""

    def __init__(self, config_path: str):
        """
        初始化分析器

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.analysis_config = self.config.get('analysis', {})
        self.risk_levels = self.config.get('risk_levels', {})
        self.signals_config = self.config.get('risk_signals', {})
        self.project_config = self.config.get('project', {})

    def calculate(self, signals: list) -> dict:
        """
        计算风险概率

        Args:
            signals: 风险信号列表

        Returns:
            分析结果
        """
        # 计算各风险概率
        risk_probabilities = {}
        for signal in signals:
            signal_dict = signal.to_dict() if hasattr(signal, 'to_dict') else signal
            prob = self._calculate_signal_probability(signal_dict)
            risk_probabilities[signal_dict['name']] = prob

        # 综合风险评分
        overall_risk = self._calculate_overall_risk(risk_probabilities)

        # 风险等级
        risk_level = self._determine_risk_level(overall_risk)

        # 优先级排序
        sorted_risks = sorted(
            risk_probabilities.items(),
            key=lambda x: x[1]['risk_score'],
            reverse=True
        )

        return {
            'project': self.project_config.get('name', '未命名项目'),
            'analysis_time': datetime.now().isoformat(),
            'overall_risk_score': round(overall_risk, 3),
            'risk_level': risk_level,
            'risk_level_info': self.risk_levels.get(risk_level, {}),
            'risk_probabilities': risk_probabilities,
            'sorted_risks': [
                {'name': name, 'risk_score': data['risk_score'],
                 'probability': data['probability'], 'impact': data['impact'],
                 'level': data['level']}
                for name, data in sorted_risks
            ],
            'top_risk': sorted_risks[0] if sorted_risks else None
        }

    def _calculate_signal_probability(self, signal: dict) -> dict:
        """
        计算单个信号的风险概率

        使用bayesian方法: P(R|S) = P(S|R) * P(R) / P(S)
        """
        prior = self.analysis_config.get('bayesian_prior', 0.3)
        exceed_rate = signal.get('exceed_rate', 0)

        # 似然比: 信号越强，条件概率越高
        likelihood = min(exceed_rate, 1.0)

        # 贝叶斯更新
        evidence_prior = prior * likelihood + (1 - prior) * (1 - likelihood)
        posterior = (likelihood * prior) / evidence_prior if evidence_prior > 0 else 0

        # 影响度评估（基于权重）
        signal_type = signal.get('type', '')
        signal_config = self.signals_config.get(signal_type, {})
        impact_weight = signal_config.get('weight', 0.1)

        # 综合风险分数
        risk_score = posterior * impact_weight * 10

        # 风险等级
        level = self._determine_risk_level(risk_score / 10)

        return {
            'name': signal.get('name', ''),
            'type': signal.get('type', ''),
            'value': signal.get('value', 0),
            'threshold': signal.get('threshold', 0),
            'probability': round(posterior, 3),
            'impact': round(impact_weight, 2),
            'risk_score': round(risk_score, 3),
            'severity': signal.get('severity', 'normal'),
            'level': level,
            'details': signal.get('details', '')
        }

    def _calculate_overall_risk(self, probabilities: dict) -> float:
        """计算综合风险评分"""
        if not probabilities:
            return 0

        # 加权平均
        total_weight = 0
        weighted_sum = 0

        for name, prob in probabilities.items():
            score = prob.get('risk_score', 0)
            weight = prob.get('impact', 0.1)
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0

    def _determine_risk_level(self, score: float) -> str:
        """判定风险等级"""
        for level_name, level_config in self.risk_levels.items():
            range_config = level_config.get('range', [0, 0.3])
            if range_config[0] <= score < range_config[1]:
                return level_name
            if score >= 1.0:
                return 'critical'
        return 'low'

    def simulate_scenarios(self, signals: list) -> dict:
        """
        模拟不同场景下的风险变化

        Args:
            signals: 风险信号列表

        Returns:
            场景模拟结果
        """
        current = self.calculate(signals)

        scenarios = {
            'best_case': self._simulate_best_case(signals),
            'worst_case': self._simulate_worst_case(signals),
            'current': current['overall_risk_score'],
            'risk_range': {
                'min': round(current['overall_risk_score'] * 0.5, 3),
                'max': round(current['overall_risk_score'] * 1.5, 3)
            }
        }

        return scenarios

    def _simulate_best_case(self, signals: list) -> dict:
        """模拟最佳场景"""
        best_signals = []
        for signal in signals:
            s = signal.to_dict() if hasattr(signal, 'to_dict') else signal.copy()
            s['exceed_rate'] = max(0, s.get('exceed_rate', 0) * 0.3)
            best_signals.append(s)

        return self.calculate(best_signals)

    def _simulate_worst_case(self, signals: list) -> dict:
        """模拟最差场景"""
        worst_signals = []
        for signal in signals:
            s = signal.to_dict() if hasattr(signal, 'to_dict') else signal.copy()
            s['exceed_rate'] = min(3.0, s.get('exceed_rate', 0) * 2)
            worst_signals.append(s)

        return self.calculate(worst_signals)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from risk_detector import RiskDetector

    detector = RiskDetector('config.yaml')
    signals = detector.detect_all()

    analyzer = RiskAnalyzer('config.yaml')
    results = analyzer.calculate(signals)

    print(f"项目: {results['project']}")
    print(f"综合风险评分: {results['overall_risk_score']}")
    print(f"风险等级: {results['risk_level']}")
    print()

    print("风险概率排序:")
    for risk in results['sorted_risks']:
        level_icon = {
            'low': '✓', 'medium': '!', 'high': '!!', 'critical': '!!!'
        }
        icon = level_icon.get(risk['level'], '?')
        print(f"  [{icon}] {risk['name']}: 概率={risk['probability']:.1%}, "
              f"分数={risk['risk_score']:.2f}")

    print(f"\n最大风险: {results['top_risk'][0] if results['top_risk'] else '无'}")

    # 场景模拟
    scenarios = analyzer.simulate_scenarios(signals)
    print(f"\n场景模拟:")
    print(f"  最佳情况: {scenarios['best_case']['overall_risk_score']:.3f}")
    print(f"  当前:     {scenarios['current']:.3f}")
    print(f"  最差情况: {scenarios['worst_case']['overall_risk_score']:.3f}")