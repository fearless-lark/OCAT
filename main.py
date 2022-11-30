import time
import numpy as np
import utils


def run(config):
    """
    Main function that calls all the support functions and produces the result
    :param config: run config (from config.ini file)
    :param echo: summary and results would be printed if echo is True
    :return: np.array of composition column names, np.array of composition scores
    """
    # read input data
    input_table_names, input_table_scores = utils.read_txt(
        config["data"]["input_table"]
    )
    adjacency_matrix_names, adjacency_matrix_indicators = utils.read_txt(
        config["data"]["adjacency_matrix"]
    )
    rules_matrix_names, rules_matrix_indicators = utils.read_txt(
        config["data"]["rules_matrix"]
    )

    if not utils.check_presence(input_table_names, config['additional_constrains']['must_have_categories'].split(', ')):
        print('Error: must have categories are not present in the Input table!')
        return None, None

    # enrich input table with 'Other' columns (if needed)
    input_table_names, input_table_scores = utils.enrich_input_table(
        input_table_scores, input_table_names
    )

    # prepare Adjacency Matrix and Rules Matrix that correspond specifically to the input table
    adjacency_matrix = utils.form_adjacency_matrix(
        input_table_names, adjacency_matrix_names, adjacency_matrix_indicators
    )
    rules_matrix = utils.form_rules_matrix(
        input_table_names, rules_matrix_names, rules_matrix_indicators
    )

    # generate all possible combinations of columns placement with restriction that one column can be assigned only once
    # (we can  treat them as branches of trees or paths of graphs, so let's call them branches)
    branches = np.array(list(utils.permutations_optimised(range(adjacency_matrix.shape[0]))))

    # apply restrictions on branches based on indicators in Adjacency Matrix and Rules Matrix
    branches_valid = utils.select_valid_branches(
        branches, rules_matrix, adjacency_matrix
    )

    # calculate scores for valid branches
    branches_scores = utils.get_branches_scores(branches_valid, input_table_scores)
    names, scores = utils.get_optimal_solution(
        branches_scores, branches_valid, input_table_names
    )

    # print summary and results
    if eval(config['run']['echo']):
        output_str = """
        Summary:
        Num columns in the Input table: {}
        Brute force approach would have to check compositions: {}
        Our approach checked compositions:
            {} on the first stage
            {} on the second stage
        Difference comparing to naive brute force approach, %: checked only {}%
        
        Optimal composition:
        Num compositions: {}
        Compositions: {}
        Compositions scores: {} {}
        """.format(
            input_table_scores.shape[1],
            input_table_scores.shape[0] ** input_table_scores.shape[1],
            branches.shape[0],
            branches_valid.shape[0],
            round(
                (branches.shape[0] + branches_valid.shape[0])
                / input_table_scores.shape[0] ** input_table_scores.shape[1]
                * 100,
                4,
            ),
            len(names),
            [[", ".join(c)] if len(names) > 1 else ", ".join(c) for c in names],
            scores if len(scores) > 1 else scores[0],
            '(same for each composition)' if len(names) > 1 else ''
        )
        print(output_str)

    return names, scores


if __name__ == "__main__":
    start = time.time()
    config = utils.get_config()
    names, scores = run(config)
    print('Wall running time:', round(time.time() - start, 2), 'sec')
