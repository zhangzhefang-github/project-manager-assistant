# 适配器模式架构实现

## 🎯 问题背景

原始实现中，prompt 模板需要明确指定 UUID 格式，违反了关注点分离原则：
- ❌ **业务逻辑层** 混合了技术实现细节
- ❌ **维护困难**：改变ID格式需要修改多个prompt模板
- ❌ **可扩展性差**：硬编码了技术实现到业务描述中

## 🏗️ 架构解决方案

### 设计原则
1. **单一职责原则**：每层专注自己的职责
2. **开闭原则**：对扩展开放，对修改封闭
3. **依赖倒置原则**：高层模块不依赖低层模块的具体实现

### 层次架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI 生成层     │    │   适配器层      │    │   业务逻辑层    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ SimpleTask      │───▶│ ModelAdapter    │───▶│ Task (UUID)     │
│ id: "task-1"    │    │ 数据转换        │    │ id: UUID(...)   │
│ 专注业务逻辑    │    │ 处理技术细节    │    │ 完整数据模型    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 文件结构

### 新增文件
- `app/schemas/simple.py` - 简化的数据模型
- `app/services/model_adapter.py` - 模型适配器服务
- `app/schemas/responses.py` - API响应模型

### 修改的文件
- `app/agent/state.py` - 添加 `id_mapping` 字段  
- `app/agent/nodes/*.py` - 所有节点使用适配器模式
- `app/api/routers/plan.py` - 更新初始状态
- `app/prompts/templates.yml` - 还原为专注业务逻辑

## 🔄 数据流

### 1. 任务生成流程
```python
# Step 1: AI 使用简化 schema
simple_tasks = llm.with_structured_output(SimpleTaskList).invoke(prompt)

# Step 2: 适配器转换
tasks, id_mapping = model_adapter.simple_to_full_task_list(simple_tasks)

# Step 3: 保存映射关系
state["id_mapping"] = id_mapping
```

### 2. 后续节点流程
```python
# Step 1: 转换为简化格式供AI使用
simple_data = model_adapter.get_simple_task_list_for_prompt(state["tasks"])

# Step 2: AI 处理简化数据
simple_result = llm.invoke(prompt_with_simple_data)

# Step 3: 适配器转换回完整格式
full_result = model_adapter.simple_to_full_xxx(simple_result, state["id_mapping"])
```

## 💡 核心优势

### ✅ 关注点分离
- **Prompt层**：专注业务逻辑描述
- **适配器层**：处理技术格式转换
- **数据层**：保持完整的类型安全

### ✅ 可维护性
```python
# 改变ID格式只需修改适配器
class ModelAdapter:
    def generate_id(self):
        return uuid.uuid4()  # 轻松切换到其他格式
```

### ✅ 可测试性
```python
# 每层可独立测试
def test_adapter():
    simple = SimpleTask(id="task-1", ...)
    full, mapping = adapter.simple_to_full_task_list(simple)
    assert mapping["task-1"] == full.tasks[0].id
```

### ✅ 扩展性
- 新增模型类型：只需扩展适配器
- 改变业务逻辑：只需修改prompt
- 改变数据格式：只需修改schema

## 🧪 验证结果

```bash
✅ 创建了 3 个简化任务
✅ 转换为 3 个完整任务  
✅ 生成ID映射: {'task-1': UUID('...'), ...}
✅ 任务验证通过: task-1 -> bd35e08b-3751-4e6a-966c-4140c5569712
🎉 适配器模式测试通过！
```

## 🚀 使用方式

### 运行系统
原有的运行方式保持不变：
```bash
python worker.py
# 或
./run.sh
```

### API调用
```bash
curl -X POST "http://localhost:8000/plans" \
  -F "project_description=..." \
  -F "team_file=@team.csv"
```

## 📈 性能影响

- **运行时开销**：微小（主要是数据转换）
- **开发效率**：显著提升（更清晰的关注点分离）
- **维护成本**：大幅降低（单一修改点）

## 🔮 未来扩展

1. **多种ID格式支持**：通过适配器配置
2. **缓存优化**：在适配器层添加缓存
3. **类型检查增强**：更严格的类型验证
4. **性能监控**：添加适配器层的性能指标

---

**结论**：适配器模式实现了真正的架构分离，让AI专注业务逻辑，让代码处理技术细节，大大提升了系统的可维护性和可扩展性。 