# Copyright (c) 2023 Anthropic
# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# This file has been modified by ByteDance Ltd. and/or its affiliates. on 13 June 2025
#
# Original file was released under MIT License, with the full license text
# available at https://github.com/anthropics/anthropic-quickstarts/blob/main/LICENSE
#
# This modified file is released under the same license.

# 顺序思考工具 - 用于分步解决复杂问题
# Sequential Thinking Tool - Step-by-step complex problem solving

import json
from dataclasses import dataclass
from typing import override

from trae_agent.tools.base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


@dataclass
class ThoughtData:
    """
    思考数据类 - 存储每一步的思考信息
    Thought data class - stores information for each thinking step
    
    属性说明：
    - thought: 当前思考内容
    - thought_number: 当前是第几步思考
    - total_thoughts: 预计总共需要多少步思考
    - next_thought_needed: 是否还需要下一步思考
    - is_revision: 是否修正了之前的想法
    - revises_thought: 如果是修正，对应修正第几步
    - branch_from_thought: 分支思考的起点
    - branch_id: 分支的唯一标识
    - needs_more_thoughts: 发现需要更多思考步骤
    """
    thought: str  # 当前思考内容
    thought_number: int  # 当前思考步骤编号（从1开始）
    total_thoughts: int  # 预计总思考步骤数
    next_thought_needed: bool  # 是否需要继续下一步思考
    is_revision: bool | None = None  # 是否为修订之前的想法
    revises_thought: int | None = None  # 修订的目标思考步骤编号
    branch_from_thought: int | None = None  # 分支思考的起点步骤
    branch_id: str | None = None  # 分支标识符
    needs_more_thoughts: bool | None = None  # 是否需要增加思考步骤


class SequentialThinkingTool(Tool):
    """
    顺序思考工具 - 用于分步解决复杂问题的AI助手工具
    Sequential Thinking Tool - AI assistant tool for solving complex problems step by step

    中文功能说明：
    这是一个帮助AI通过分步思考来解决复杂问题的工具。它允许AI像人类一样逐步分析问题，
    在过程中可以修正错误、回溯思路、创建分支思考，并动态调整思考深度。

    核心特性：
    1. 分步思考：将复杂问题分解为多个小步骤
    2. 动态修正：可以质疑和修正之前的想法
    3. 分支分析：从不同角度创建思考分支
    4. 深度调整：根据进展增加或减少思考步骤
    5. 验证循环：生成假设→验证→修正→再验证

    使用场景：
    - 复杂编程任务分析和规划
    - 调试过程中的问题定位
    - 算法设计和优化
    - 架构决策的多方案比较
    - 需要深度分析的疑难问题解决
    
    This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
    Each thought can build on, question, or revise previous insights as understanding deepens.
    """

    @override
    def get_name(self) -> str:
        return "sequentialthinking"

    @override
    def get_description(self) -> str:
        return """
        【中文详细说明】顺序思考工具 - AI的"思维笔记本"
        
        这个工具帮助AI像人类专家一样，通过逐步分析来解决复杂问题。它不是一个简单的线性思考工具，
        而是一个支持动态修正、分支探索和深度调整的智能化思考系统。

        ## 核心概念
        1. **分步思考**：将大问题拆分为可管理的小步骤
        2. **动态修正**：发现错误时可以回溯修改之前的想法
        3. **分支探索**：从不同角度同时分析问题
        4. **深度自适应**：根据问题复杂度调整思考深度

        ## 使用场景（什么时候用这个工具）
        - 🔍 复杂编程任务：需要多步分析和规划
        - 🐛 调试疑难杂症：逐步定位问题根因
        - 🏗️ 架构设计：比较多种技术方案的优劣
        - 📊 算法优化：分析性能瓶颈和改进路径
        - 🤔 需求分析：澄清模糊或复杂的业务需求
        - 📋 代码审查：系统性检查代码质量问题

        ## 参数详细说明

        ### 必需参数
        - **thought** (当前思考内容): 
          这一步的具体思考，可以是分析、质疑、修正或新发现
          例如："首先分析这个bug的复现条件..."

        - **next_thought_needed** (是否需要下一步):
          true表示还需要继续思考，false表示已经得到满意答案

        - **thought_number** (当前步骤编号):
          从1开始的序号，记录这是第几步思考

        - **total_thoughts** (预计总步骤数):
          初始估计，可以根据实际情况动态调整

        ### 可选参数（高级功能）
        - **is_revision** (是否修正之前想法):
          true表示这一步修正了之前的某个想法

        - **revises_thought** (修正的目标步骤):
          如果is_revision为true，这里指定修正第几步

        - **branch_from_thought** (分支起点):
          从第几步开始创建新的思考分支

        - **branch_id** (分支标识):
          给这个分支起个名字，便于追踪

        - **needs_more_thoughts** (发现需要更多步骤):
          当发现比预期更复杂时标记为true

        ## 使用技巧
        1. **开始阶段**：先给出合理的总步骤估计
        2. **中期调整**：发现复杂度变化时及时调整total_thoughts
        3. **修正机制**：大胆质疑和修正之前的想法
        4. **分支策略**：对不确定的部分创建平行分析
        5. **收敛判断**：确保最终答案经过充分验证

        ## 实际工作流程示例
        ```
        步骤1: 理解问题范围和约束条件
        步骤2: 分析可能的解决方案
        步骤3: 评估各方案的优缺点
        步骤4: 选择最优方案并细化
        步骤5: 验证方案的可行性
        步骤6: 总结最终解决方案
        ```

        【English Description】A detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
* Regular analytical steps
* Revisions of previous thoughts
* Questions about previous decisions
* Realizations about needing more analysis
* Changes in approach
* Hypothesis generation
* Hypothesis verification
- next_thought_needed: True if you need more thinking, even if at what seemed like the end
- thought_number: Current number in sequence (can go beyond initial total)
- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
- is_revision: A boolean indicating if this thought revises previous thinking
- revises_thought: If is_revision is true, which thought number is being reconsidered
- branch_from_thought: If branching, which thought number is the branching point
- branch_id: Identifier for the current branch (if any)
- needs_more_thoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached"""

    @override
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="thought",
                type="string",
                description="Your current thinking step",
                required=True,
            ),
            ToolParameter(
                name="next_thought_needed",
                type="boolean",
                description="Whether another thought step is needed",
                required=True,
            ),
            ToolParameter(
                name="thought_number",
                type="integer",
                description="Current thought number. Minimum value is 1.",
                required=True,
            ),
            ToolParameter(
                name="total_thoughts",
                type="integer",
                description="Estimated total thoughts needed. Minimum value is 1.",
                required=True,
            ),
            ToolParameter(
                name="is_revision",
                type="boolean",
                description="Whether this revises previous thinking",
            ),
            ToolParameter(
                name="revises_thought",
                type="integer",
                description="Which thought is being reconsidered. Minimum value is 1.",
            ),
            ToolParameter(
                name="branch_from_thought",
                type="integer",
                description="Branching point thought number. Minimum value is 1.",
            ),
            ToolParameter(
                name="branch_id",
                type="string",
                description="Branch identifier",
            ),
            ToolParameter(
                name="needs_more_thoughts",
                type="boolean",
                description="If more thoughts are needed",
            ),
        ]

    def __init__(self, model_provider: str | None = None) -> None:
        super().__init__(model_provider)
        self.thought_history: list[ThoughtData] = []
        self.branches: dict[str, list[ThoughtData]] = {}

    @override
    def get_model_provider(self) -> str | None:
        return self._model_provider

    def _validate_thought_data(self, arguments: ToolCallArguments) -> ThoughtData:
        """Validate the input arguments and return a ThoughtData object."""
        if "thought" not in arguments or not isinstance(arguments["thought"], str):
            raise ValueError("Invalid thought: must be a string")

        if "thought_number" not in arguments or not isinstance(arguments["thought_number"], int):
            raise ValueError("Invalid thought_number: must be a number")

        if "total_thoughts" not in arguments or not isinstance(arguments["total_thoughts"], int):
            raise ValueError("Invalid total_thoughts: must be a number")

        if "next_thought_needed" not in arguments or not isinstance(
            arguments["next_thought_needed"], bool
        ):
            raise ValueError("Invalid next_thought_needed: must be a boolean")

        # Validate minimum values
        if arguments["thought_number"] < 1:
            raise ValueError("thought_number must be at least 1")

        if arguments["total_thoughts"] < 1:
            raise ValueError("total_thoughts must be at least 1")

        # Validate optional revision fields
        if (
            "revises_thought" in arguments
            and arguments["revises_thought"] is not None
            and arguments["revises_thought"] != 0
        ):
            if (
                not isinstance(arguments["revises_thought"], int)
                or arguments["revises_thought"] < 1
            ):
                raise ValueError("revises_thought must be a positive integer")
            else:
                revises_thought = int(arguments["revises_thought"])
        else:
            revises_thought = None

        if (
            "branch_from_thought" in arguments
            and arguments["branch_from_thought"] is not None
            and arguments["branch_from_thought"] != 0
        ):
            if (
                not isinstance(arguments["branch_from_thought"], int)
                or arguments["branch_from_thought"] < 1
            ):
                raise ValueError("branch_from_thought must be a positive integer")
            else:
                branch_from_thought = int(arguments["branch_from_thought"])
        else:
            branch_from_thought = None

        # Extract and cast the validated values
        thought = str(arguments["thought"])
        thought_number = int(arguments["thought_number"])  # Already validated as int
        total_thoughts = int(arguments["total_thoughts"])  # Already validated as int
        next_thought_needed = bool(arguments["next_thought_needed"])  # Already validated as bool

        # Handle optional fields with proper type checking
        is_revision = None
        branch_id = None
        needs_more_thoughts = None

        if "is_revision" in arguments and arguments["is_revision"] is not None:
            is_revision = bool(arguments["is_revision"])

        if "branch_id" in arguments and arguments["branch_id"] is not None:
            branch_id = str(arguments["branch_id"])

        if "needs_more_thoughts" in arguments and arguments["needs_more_thoughts"] is not None:
            needs_more_thoughts = bool(arguments["needs_more_thoughts"])

        return ThoughtData(
            thought=thought,
            thought_number=thought_number,
            total_thoughts=total_thoughts,
            next_thought_needed=next_thought_needed,
            is_revision=is_revision,
            revises_thought=revises_thought,
            branch_from_thought=branch_from_thought,
            branch_id=branch_id,
            needs_more_thoughts=needs_more_thoughts,
        )

    def _format_thought(self, thought_data: ThoughtData) -> str:
        """Format a thought for display with visual styling."""
        prefix = ""
        context = ""

        if thought_data.is_revision:
            prefix = "🔄 Revision"
            context = f" (revising thought {thought_data.revises_thought})"
        elif thought_data.branch_from_thought:
            prefix = "🌿 Branch"
            context = (
                f" (from thought {thought_data.branch_from_thought}, ID: {thought_data.branch_id})"
            )
        else:
            prefix = "💭 Thought"
            context = ""

        header = f"{prefix} {thought_data.thought_number}/{thought_data.total_thoughts}{context}"
        border_length = max(len(header), len(thought_data.thought)) + 4
        border = "─" * border_length

        return f"""
┌{border}┐
│ {header.ljust(border_length - 2)} │
├{border}┤
│ {thought_data.thought.ljust(border_length - 2)} │
└{border}┘"""

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Execute the sequential thinking tool."""
        try:
            # Validate and extract thought data
            validated_input = self._validate_thought_data(arguments)

            # Adjust total thoughts if current thought number exceeds it
            if validated_input.thought_number > validated_input.total_thoughts:
                validated_input.total_thoughts = validated_input.thought_number

            # Add to thought history
            self.thought_history.append(validated_input)

            # Handle branching
            if validated_input.branch_from_thought and validated_input.branch_id:
                if validated_input.branch_id not in self.branches:
                    self.branches[validated_input.branch_id] = []
                self.branches[validated_input.branch_id].append(validated_input)

            # Format and display the thought
            # formatted_thought = self._format_thought(validated_input)
            # print(formatted_thought, flush=True)  # Print to stdout for immediate feedback

            # Prepare response
            response_data = {
                "thought_number": validated_input.thought_number,
                "total_thoughts": validated_input.total_thoughts,
                "next_thought_needed": validated_input.next_thought_needed,
                "branches": list(self.branches.keys()),
                "thought_history_length": len(self.thought_history),
            }

            return ToolExecResult(
                output=f"Sequential thinking step completed.\n\nStatus:\n{json.dumps(response_data, indent=2)}"
            )

        except Exception as e:
            error_data = {"error": str(e), "status": "failed"}
            return ToolExecResult(
                error=f"Sequential thinking failed: {str(e)}\n\nDetails:\n{json.dumps(error_data, indent=2)}",
                error_code=-1,
            )
