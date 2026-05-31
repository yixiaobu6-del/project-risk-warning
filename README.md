# 项目风险早期预警

在项目风险爆发之前识别预警信号，实现主动风险管理。

## 项目简介

项目风险往往在爆发之前就有蛛丝马迹——成员疲惫、沟通延迟、进度偏差等。本工具通过系统性监控项目的多维数据，识别风险信号，计算风险发生概率，实现"防患于未然"的风险管理。

## 核心功能

- **风险信号检测**：实时监控项目状态，捕捉风险前兆
- **概率计算**：基于历史数据和贝叶斯更新计算风险发生概率
- **报告生成**：生成可视化预警报告
- **风险分类**：按类别和严重程度对风险进行分级
- **应对建议**：针对不同风险类型提供应对策略

## 技术架构

```
项目风险早期预警/
├── config.yaml              # 配置文件
├── risk_detector.py         # 风险信号检测框架
├── analyzer.py              # 概率计算
├── reporter.py              # 报告生成
├── requirements.txt
└── README.md
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行检测

```bash
python risk_detector.py
python analyzer.py
python reporter.py
```

### Python调用

```python
from risk_detector import RiskDetector
from analyzer import RiskAnalyzer
from reporter import RiskReporter

# 检测风险信号
detector = RiskDetector("config.yaml")
signals = detector.detect_all()

# 分析概率
analyzer = RiskAnalyzer("config.yaml")
probabilities = analyzer.calculate(signals)

# 生成报告
reporter = RiskReporter("config.yaml", probabilities)
reporter.generate()
```

## 风险信号类型

| 类别 | 信号 | 监控指标 |
|------|------|----------|
| 进度风险 | 里程碑延迟 | 计划完成率偏差 |
| 质量风险 | Bug率上升 | 缺陷密度趋势 |
| 团队风险 | 人员流动 | 成员活跃度变化 |
| 沟通风险 | 信息延迟 | 响应时间增长 |
| 成本风险 | 预算超支 | 资源消耗速率 |

## 配置示例

```yaml
risk_signals:
  schedule_delay:
    threshold_days: 3
    weight: 0.3
  bug_density:
    threshold_per_kloc: 5
    weight: 0.25
  team_churn:
    threshold_rate: 0.1
    weight: 0.2
```

## 应用场景

- **项目管理办公室**：同时监控多个项目健康状态
- **IT项目**：跟踪开发进度和技术风险
- **产品交付**：确保产品按时交付的质量风险
- **项目组合管理**：评估项目组合的整体风险水平

## 许可证

MIT License