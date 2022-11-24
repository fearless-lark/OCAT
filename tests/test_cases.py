import numpy as np
import pytest
import utils
from main import run


config = utils.get_config()


@pytest.mark.parametrize('case_path', ['./cases/case1.txt'])
def test_case1(case_path):
    config['data']['input_table'] = case_path
    names, scores = run(config, echo=True)
    ground_truth = np.array(
        ['Description', 'Rate', 'CurrentAmount']
    )
    assert all(np.array(names[0]) == ground_truth)
    assert scores[0] == 8


@pytest.mark.parametrize('case_path', ['./cases/case2.txt'])
def test_case2(case_path):
    config['data']['input_table'] = case_path
    names, scores = run(config, echo=True)
    ground_truth = np.array(
        ['Description', 'CurrentAmount', 'YtdAmount']
    )
    assert all(np.array(names[0]) == ground_truth)
    assert scores[0] == 8


@pytest.mark.parametrize('case_path', ['./cases/case3.txt'])
def test_case3(case_path):
    config['data']['input_table'] = case_path
    names, scores = run(config, echo=True)
    ground_truth = np.array(
        ['Description', 'CurrentHours', 'YtdHours', 'CurrentAmount', 'YtdAmount']
    )
    assert all(np.array(names[0]) == ground_truth)
    assert scores[0] == 14


@pytest.mark.parametrize('case_path', ['./cases/case4.txt'])
def test_case4(case_path):
    config['data']['input_table'] = case_path
    names, scores = run(config, echo=True)
    ground_truth = np.array(
        ['Description', 'Other', 'Other', 'Rate', 'CurrentHours', 'CurrentAmount', 'YtdHours', 'YtdAmount']
    )
    assert all(np.array(names[0]) == ground_truth)
    assert scores[0] == 21
