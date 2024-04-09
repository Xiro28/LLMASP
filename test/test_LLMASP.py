
from ExecutorHandler import ExecutorHandler
import pytest
from unittest.mock import MagicMock, patch
from LLMASP.src.LLMASP import LLMASP


@pytest.fixture
def llmasp_fix():
    with patch.object(LLMASP, '__loadConfig__',
                       side_effect=[{"preprocessing": [{"prompt": "§ Test request", "predicate": "test(x)."}]}, 
                                      [{"prompt": "Test request", "response": "test(x)."}]]):
        return LLMASP("config.yml", "rag_db.yml", "code.asp")

def test_to_gpt_dict(llmasp_fix):
    gpt_dict = llmasp_fix.__toGPTDict__("some text")
    assert gpt_dict == {"role": "user", "content": "some text"}


def test_filter_asp_atoms(llmasp_fix):
    filtered_req = llmasp_fix.__filterASPAtoms__("some random text\nrequest(x).\nrandom")
    assert filtered_req == "request(x)."

def test_not_runnable_ExecutorHandler():
    exec_handler = ExecutorHandler("config.yml", "rag_db.yml", "code.asp")
    with pytest.raises(NotImplementedError):
        exec_handler.run()

def test_inputSeasoning(llmasp_fix):
    assert "[USER_INPUT]random text[/USER_INPUT]" in llmasp_fix.__preInputSeasoning__("random text")


def test_get_empty_info(llmasp_fix):
    assert llmasp_fix.getEvaluator().getInfo() == "Atoms extracted: \nAtoms calculated: "

def test_run_asp_with_empty_preds(llmasp_fix):
    llmasp_fix.preds = ""
    mocked_file = MagicMock()
    mocked_file.read.return_value = "res(x) :- test(x)."
    with patch('builtins.open', return_value=mocked_file):
        result = llmasp_fix.runASP()
    assert str(result.calc_preds) == ""

def test_run_asp_with_non_empty_preds(llmasp_fix):
    llmasp_fix.preds = "test(x)."
    mocked_file = MagicMock()
    mocked_file.read.return_value = "res(x) :- test(x)."
    with patch('builtins.open', return_value=mocked_file):
        result = llmasp_fix.runASP()
    assert str(result.calc_preds) == "test(x) res(x)"
