# Advanced Modes

Use these extensions only when explicitly requested.

## 1) UML + Class Diagram
### Additional Tasks
- Generate a compact class/component diagram for core modules.
- Show ownership and dependency direction.

### Output Add-on
- Add section: `# 八、类图/组件图（可选）`
- Include PlantUML for class/component view.

## 2) Interview Q&A Set
### Additional Tasks
- Generate role-specific questions (backend, infra, agent system).
- Include expected strong answer points and common weak answers.

### Output Add-on
- Add section: `# 八、面试问答（扩展）`
- Format each item as: `Q`, `What interviewer wants`, `Strong answer`.

## 3) Debug Entrypoint Map
### Additional Tasks
- Identify first-check functions for failures in startup, runtime, and output stages.
- Map symptom -> likely module -> first file/function to inspect.

### Output Add-on
- Add section: `# 八、Debug 入口定位`
- Include a triage table with priority order.

## 4) Architecture Comparison
### Additional Tasks
- Compare architecture at the same abstraction level (layering, state model, orchestration style, failure handling).
- Avoid feature checklist comparisons.

### Output Add-on
- Add section: `# 八、架构对比`
- Use dimensions: execution model, state handling, extensibility, reliability, operational complexity.

## Guardrails
- Keep the base seven sections unchanged.
- Clearly mark comparison assumptions when codebases differ in scope.
- Do not claim parity where evidence is missing.
