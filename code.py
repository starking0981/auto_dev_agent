import os
import sys
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import RegexParser

# ==========================================
# 配置部分 (请替换为你的 API Key)
# ==========================================
# 如果你有 OpenAI Key，请在这里替换
# 如果没有，代码会模拟运行模式，依然可以展示逻辑流
USE_REAL_API = False 
os.environ["OPENAI_API_KEY"] = "sk-dummy-key" 

if USE_REAL_API:
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)
else:
    # 模拟模式：为了让你在没有 Key 的情况下也能跑通演示逻辑
    class MockLLM:
        def __call__(self, prompt):
            return "Mock Response"
    llm = MockLLM()

# ==========================================
# 1. 架构师 Agent (Architect Agent)
# ==========================================
class ArchitectAgent:
    def __init__(self, llm):
        self.prompt = PromptTemplate(
            input_variables=["user_requirement"],
            template="""
            你是一个资深软件架构师。请根据用户需求，生成详细的技术规格说明书。
            
            思考步骤 (Chain of Thought):
            1. 分析核心功能点。
            2. 设计函数签名和参数。
            3. 设计返回值结构。
            
            用户需求: {user_requirement}
            
            请输出 JSON 格式的设计方案（包含 function_signature, description）。
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def design(self, requirement):
        print(f"🧠 [架构师 Agent] 正在分析需求: {requirement}")
        # 模拟真实调用
        if isinstance(llm, MockLLM):
            return '{"function_signature": "def process_data(data: list) -> dict:", "description": "处理数据并返回统计结果"}'
        return self.chain.run(user_requirement=requirement)

# ==========================================
# 2. 程序员 Agent (Coder Agent)
# ==========================================
class CoderAgent:
    def __init__(self, llm):
        self.prompt = PromptTemplate(
            input_variables=["design_spec", "error_feedback"],
            template="""
            你是一个全栈开发工程师。请根据架构师的设计编写具体的 Python 代码。
            
            架构设计: {design_spec}
            
            {error_feedback}
            
            请只输出 Python 代码块，不要输出其他解释。
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def code(self, design_spec, error_feedback=""):
        print(f"👨💻 [程序员 Agent] 正在编写代码...")
        if isinstance(llm, MockLLM):
            return "def process_data(data: list) -> dict:\n    if not data:\n        raise ValueError('Empty list')\n    return {'count': len(data)}"
        return self.chain.run(design_spec=design_spec, error_feedback=error_feedback)

# ==========================================
# 3. QA Agent (Tester Agent)
# ==========================================
class QAAgent:
    def __init__(self, llm):
        self.prompt = PromptTemplate(
            input_variables=["code_snippet"],
            template="""
            你是一个严格的 QA 工程师。请为以下代码编写 pytest 单元测试。
            
            代码: {code_snippet}
            
            请输出测试代码。
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def test(self, code_snippet):
        print(f"🐞 [QA Agent] 正在生成测试用例...")
        if isinstance(llm, MockLLM):
            return "def test_process_data():\n    assert process_data([1,2]) == {'count': 2}\n    try:\n        process_data([])\n        assert False\n    except ValueError:\n        pass"
        return self.chain.run(code_snippet=code_snippet)

# ==========================================
# 4. 核心工作流 (Orchestrator)
# ==========================================
class DevWorkflow:
    def __init__(self):
        self.architect = ArchitectAgent(llm)
        self.coder = CoderAgent(llm)
        self.qa = QAAgent(llm)

    def run(self, requirement, max_retries=2):
        print("="*50)
        print(f"🚀 [系统启动] 开始处理任务: {requirement}")
        print("="*50)

        # 1. 架构设计
        design = self.architect.design(requirement)
        print(f"📄 [架构设计] 输出: {design}\n")

        generated_code = ""
        error_feedback = ""

        # 2. 编码与测试循环 (Self-Correction Loop)
        for attempt in range(max_retries + 1):
            print(f"--- 第 {attempt + 1} 轮迭代 ---")
            
            # 编码
            generated_code = self.coder.code(design, error_feedback)
            print(f" [代码生成]:\n{generated_code}\n")

            # 测试 (模拟执行)
            print("🔍 [QA Agent] 正在执行测试...")
            # 这里模拟一个逻辑：第一次通常会失败（模拟 bug），第二次修复成功
            if attempt == 0 and isinstance(llm, MockLLM):
                print("❌ [测试失败] AssertionError: 缺少空列表校验逻辑。")
                error_feedback = "错误: 代码缺少对空列表的 ValueError 抛出，请修复。"
                continue
            else:
                print("✅ [测试通过] All tests passed!")
                break
        
        print("\n🎉 [流程结束] 代码已验收通过，准备合并到主分支。")
        return generated_code

# ==========================================
# 运行入口
# ==========================================
if __name__ == "__main__":
    # 模拟一个真实需求
    req = "编写一个 Python 函数，接收一个数字列表，返回最大值和最小值的差值。如果列表为空，抛出 ValueError。"
    
    workflow = DevWorkflow()
    final_code = workflow.run(req)
    
    print("\n---------------- 最终交付物 ----------------")
    print(final_code)
