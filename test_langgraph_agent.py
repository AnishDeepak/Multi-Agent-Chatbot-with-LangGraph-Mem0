import pytest

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import (
    TaskCompletionMetric,
    StepEfficiencyMetric,
    PlanAdherenceMetric,
)
from deepeval.models import OllamaModel
from graph import build_graph
from database import checkpointer

judge_model = OllamaModel(
    model="gemma4:cloud",
    base_url="http://localhost:11434",
    temperature=0
)
graph = build_graph(checkpointer)


test_cases = [
    Golden(
        input="What is the current weather in Vizag?"
    ),
    Golden(
        input="Explain the skills mentioned in my resume."
    ),
    
]


@pytest.mark.parametrize("golden", test_cases)
def test_langgraph_agent(golden):

    callback = CallbackHandler(
        name="multi-agent-evaluation",
        tags=["langgraph", "agent-evaluation"],
    )

    config = {
        "configurable": {
            "thread_id": "evaluation-thread"
        },
        "callbacks": [callback],
    }

    graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": golden.input,
                }
            ],
            "worker_called": "",
        },
        config=config,
    )

    metrics = [
    TaskCompletionMetric(model=judge_model),
    StepEfficiencyMetric(model=judge_model),
    PlanAdherenceMetric(model=judge_model),]

    assert_test(
        golden=golden,
        metrics=metrics,
    )