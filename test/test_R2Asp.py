from io import StringIO
import pytest
from unittest.mock import MagicMock, patch
from R2Asp import R2Asp

@pytest.fixture
def r2asp_instance():
    return R2Asp()

def test_load_config(mocker, r2asp_instance):
    with patch('builtins.open', MagicMock(return_value=StringIO('predicates:\n  input:\n    - foo\narguments:\n  foo:\n    request: "Request"\n    data_type: "Type"'))):
        config = r2asp_instance._R2Asp__loadConfig__('config.yml')
    assert config == {'predicates': {'input': ['foo']}, 'arguments': {'foo': {'request': 'Request', 'data_type': 'Type'}}}

def test_user_input_to_gpt(r2asp_instance):
    text = "some text"
    output = r2asp_instance._R2Asp__userInputToGPT__(text)
    assert output == {"role": "user", "content": text}

def test_get_code_from_response(r2asp_instance):
    response = "```code```"
    code = r2asp_instance._R2Asp__getCodeFromResponse__(response)
    assert code == "code"

def test_clean_output_request(r2asp_instance):
    req = "```code```"
    cleaned_req = r2asp_instance._R2Asp__cleanOutputRequest__(req)
    assert cleaned_req == "code"

def test_request_body(r2asp_instance):
    user_input = "some input"
    with patch.object(R2Asp, '_R2Asp__userInputToGPT__', return_value={"role": "user", "content": "request"}):
        body = r2asp_instance._R2Asp__request_body__(user_input)
    assert body == {"role": "user", "content": "request"}

def test_make_request(r2asp_instance):
    user_input = "some input"
    with patch.object(R2Asp, '_R2Asp__userInputToGPT__', return_value={"role": "user", "content": "request"}):
        with patch('g4f.ChatCompletion.create', MagicMock()):
            response = r2asp_instance._R2Asp__makeRequest__(user_input)
    assert isinstance(response, tuple)
    assert len(response) == 2
