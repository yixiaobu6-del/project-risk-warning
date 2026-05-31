"""
项目风险早期预警 - 风险信号检测框架
检测项目中的各类风险预警信号
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml


class RiskSignal:
    """风险信号数据类"""

    def __init__(self, signal_type: str, name: str, value: float,
                 threshold: float, severity: str, details: str):
        self.signal_type = signal_type
        self.name = name
        self.value = value
        self.threshold = threshold
        self.severity = severity
        self.details = details
        self.timestamp = datetime.now().isoformat()
        self.exceed_rate = min(value / threshold, 3.0) if threshold > 0 else 0

    def to_dict(self) -> dict:
        return {
            'type': self.signal_type,
            'name': self.name,
            'value': self.value,
            'threshold': self.threshold,
            'severity': self.severity,
            'details': self.details,
            'timestamp': self.timestamp,
            'exceed_rate': round(self.exceed_rate, 2)
        }


class RiskDetector:
    """风险信号检测器"""

    def __init__(self, config_path: str):
        """
        初始化检测器

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.signals_config = self.config.get('risk_signals', {})
        self.signals = []

    def detect_all(self) -> list:
        """检测所有风险信号"""
        self.signals = []

        for signal_type, config in self.signals_config.items():
            if not config.get('enabled', True):
                continue

            detector_method = getattr(self, f'_detect_{signal_type}', None)
            if detector_method:
                try:
                    signal = detector_method(config)
                    if signal:
                        self.signals.append(signal)
                except Exception as e:
                    print(f"[检测] 检测{signal_type}时出错: {e}")

        return self.signals

    def _detect_schedule_delay(self, config: dict) -> Optional[RiskSignal]:
        """检测进度延迟"""
        threshold = config.get('threshold_days', 3)
        warning = config.get('warning_days', 2)

        # 模拟进度数据
        delay_days = 4.5

        severity = self._determine_severity(delay_days, threshold, warning)

        details = f"当前进度延迟 {delay_days} 天（阈值: {threshold} 天），延期率: {round(delay_days / threshold * 100)}%"

        return RiskSignal(
            signal_type='schedule_delay',
            name=config['name'],
            value=delay_days,
            threshold=threshold,
            severity=severity,
            details=details
        )

    def _detect_bug_density(self, config: dict) -> Optional[RiskSignal]:
        """检测缺陷密度"""
        threshold = config.get('threshold_per_kloc', 5)
        warning = config.get('warning_per_kloc', 3)

        # 模拟Bug数据
        bug_density = 3.8

        severity = self._determine_severity(bug_density, threshold, warning)

        details = f"当前Bug密度: {bug_density}/KLOC（阈值: {threshold}/KLOC），趋势: 上升"

        return RiskSignal(
            signal_type='bug_density',
            name=config['name'],
            value=bug_density,
            threshold=threshold,
            severity=severity,
            details=details
        )

    def _detect_team_churn(self, config: dict) -> Optional[RiskSignal]:
        """检测人员流动"""
        threshold = config.get('threshold_rate', 0.1)
        warning = config.get('warning_rate', 0.05)

        # 模拟人员流动数据
        churn_rate = 0.08

        severity = self._determine_severity(churn_rate, threshold, warning)

        details = f"当前人员流动率: {churn_rate:.1%}（阈值: {threshold:.0%}）"

        return RiskSignal(
            signal_type='team_churn',
            name=config['name'],
            value=churn_rate,
            threshold=threshold,
            severity=severity,
            details=details
        )

    def _detect_communication_delay(self, config: dict) -> Optional[RiskSignal]:
        """检测沟通延迟"""
        threshold = config.get('threshold_hours', 24)
        warning = config.get('warning_hours', 12)

        # 模拟沟通数据
        delay_hours = 18.5

        severity = self._determine_severity(delay_hours, threshold, warning)

        details = f"关键消息平均响应时间: {delay_hours}小时（阈值: {threshold}小时）"

        return RiskSignal(
            signal_type='communication_delay',
            name=config['name'],
            value=delay_hours,
            threshold=threshold,
            severity=severity,
            details=details
        )

    def _detect_cost_overrun(self, config: dict) -> Optional[RiskSignal]:
        """检测成本超支"""
        threshold = config.get('threshold_percent', 10)
        warning = config.get('warning_percent', 5)

        # 模拟成本数据
        overrun_percent = 7.2

        severity = self._determine_severity(overrun_percent, threshold, warning)

        details = f"当前成本超支: {overrun_percent}%（阈值: {threshold}%）"

        return RiskSignal(
            signal_type='cost_overrun',
            name=config['name'],
            value=overrun_percent,
            threshold=threshold,
            severity=severity,
            details=details
        )

    def _detect_requirement_churn(self, config: dict) -> Optional[RiskSignal]:
        """检测需求变更"""
        threshold = config.get('threshold_count', 5)
        warning = config.get('warning_count', 3)

        # 模拟需求变更数据
        churn_count = 4

        severity = self._determine_severity(churn_count, threshold, warning)

        details = f"本月需求变更次数: {churn_count}（阈值: {threshold}次/月）"

        return RiskSignal(
            signal_type='requirement_churn',
            name=config['name'],
            value=churn_count,
            threshold=threshold,
            severity=severity,
            details=details
        )

    def _determine_severity(self, value: float, threshold: float,
                            warning: float) -> str:
        """判定信号严重程度"""
        if value >= threshold:
            return 'critical'
        elif value >= warning:
            return 'warning'
        else:
            return 'normal'

    def get_active_signals(self) -> list:
        """获取活跃预警信号"""
        return [s for s in self.signals if s.severity in ('warning', 'critical')]

    def get_summary(self) -> dict:
        """获取检测汇总"""
        severity_counts = {'normal': 0, 'warning': 0, 'critical': 0}
        for signal in self.signals:
            severity_counts[signal.severity] = severity_counts.get(signal.severity, 0) + 1

        return {
            'total_signals': len(self.signals),
            'active_warnings': severity_counts.get('warning', 0),
            'active_critical': severity_counts.get('critical', 0),
            'severity_distribution': severity_counts,
            'detected_at': datetime.now().isoformat()
        }


if __name__ == '__main__':
    detector = RiskDetector('config.yaml')
    signals = detector.detect_all()

    print(f"检测到 {len(signals)} 个风险信号:")
    for signal in signals:
        severity_icon = {'normal': '✓', 'warning': '!', 'critical': '!!'}
        d = signal.to_dict()
        print(f"  [{severity_icon.get(d['severity'], '?')}] {d['name']}: {d['details']}")

    summary = detector.get_summary()
    print(f"\n汇总: 共{summary['total_signals']}个信号, "
          f"警告{summary['active_warnings']}个, "
          f"严重{summary['active_critical']}个")