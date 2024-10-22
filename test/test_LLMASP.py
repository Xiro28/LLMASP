import pytest
from unittest.mock import MagicMock, patch
from src.LLMASP import LLMASP

from src.outputHandlers.executeOutput import ExecuteOutput
from src.inputHandlers.evaluateInput import EvaluateInput
from src.inputHandlers.abstractInputHandler import AbstractInputHandler
from src.outputHandlers.evaluateOutput import EvaluateOuput
from src.utils.LLMHandler import LLMHandler



@pytest.fixture
def llmasp_fix():
    with patch.object(LLMASP, '__load_config__',
                       side_effect=[{
                           "preprocessing": [{"_": "Test request"}, {"test(x).": "Test predicate"}],
                           "knowledge_base": "res(x) :- test(x)."
                           }]):
        return LLMASP(EvaluateInput, '')

def test_to_gpt_user_dict():
    gpt_dict = LLMHandler("test").__to_gpt_user_dict__("some text")
    assert gpt_dict == {"role": "user", "content": "some text"}

def test_to_gpt_system_dict():
    gpt_dict = LLMHandler("test").__to_gpt_system_dict__("some text")
    assert gpt_dict == {"role": "system", "content": "some text"}

def test_filter_asp_atoms():
    filtered_req = AbstractInputHandler({}, "test").__filter_asp_atoms__("some random text\ntest:request(x).\nrandom")
    assert filtered_req == "request(x)."

def test_not_runnable_ExecutorHandler(llmasp_fix):
    with pytest.raises(NotImplementedError):
        llmasp_fix._as(ExecuteOutput).run()

def test_get_empty_info(llmasp_fix):
    with pytest.raises(AssertionError):
        llmasp_fix._as(EvaluateOuput).getInfo()

def test_run_asp_with_none_calc_preds(llmasp_fix):
    llmasp_fix.preds = "asp(x)."
    mocked_file = MagicMock()
    mocked_file.read.return_value = "res(x) :- test(x)."
    with patch('builtins.open', return_value=mocked_file):
        result = llmasp_fix.run_asp()
    assert str(result.calc_preds) == "asp(x)."

def test_run_asp_with_non_empty_preds(llmasp_fix):
    llmasp_fix.preds = "test(x)."
    result = llmasp_fix.run_asp()
    assert str(result.calc_preds) == "test(x).\nres(x)."
