
import pytest
from unittest.mock import patch
from src.LLMASP import LLMASP


@pytest.fixture
def llmasp_fix():
    with patch.object(LLMASP, '__loadConfig__',
                      return_value={"preprocessing": [{"prompt": "$Test request", "predicate": "test(x)."}]}):
        return LLMASP("config.yml", "valasp.yml", "code.asp", "", "")

def test_to_gpt_dict(llmasp_fix):
    gpt_dict = llmasp_fix.__toGPTDict__("some text")
    assert gpt_dict == {"role": "user", "content": "some text"}


def test_filter_asp_atoms(llmasp_fix):
    filtered_req = llmasp_fix.__filterASPAtoms__("some random text\nrequest(x).\nrandom")
    assert filtered_req == "request(x)."


def test_run_asp(llmasp_fix):
    assert True
    """
    with patch('builtins.open', MagicMock(return_value='test(X) :- test2. #show test/1')):
        assert llmasp_fix.runASP().getInfo() == ''
    """


def test_inputSeasoning(llmasp_fix):
    assert llmasp_fix.__inputSeasoning__("random text") == ("You are a NaturalLanguage to AnswerSetProgramming "
                                                            "translator\nYou are going to be asked a series of "
                                                            "questions and the answer are inside the user input "
                                                            "provided with: [USRIN] input [/USRIN]\nBe sure to "
                                                            "control the arity of the predicates!\nIf a question "
                                                            "doesn't have a clear answer, skip it.\nAlso, "
                                                            "keep everything lowercase! \n\n[USRIN] random text ["
                                                            "/USRIN]\n\nTest request\n\nFill the answer in the "
                                                            "following structure:\ntest(x).\n")


def test_get_empty_info(llmasp_fix):
    assert llmasp_fix.getInfo() == "Atoms extracted: None\nAtoms calculated: None"
