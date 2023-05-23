import configparser
import numpy as np


def get_config(config_path="config.ini"):
    """
    Read config.ini file.
    :param config_path: path to config.ini
    :return: dict with config names and values
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def read_txt(file_path):
    """
    Read input txt files in form of matrices,
    where values are separated with tabs,
    and first column is row names
    :param file_path: path to txt file
    :return: np.array of table names, np.array of table scores
    """
    # read txt
    mat = np.loadtxt(file_path, dtype="U", delimiter="\t")
    # extract names
    names = mat[:, 0]
    # extract scores
    scores = mat[:, 1:].astype(int)
    return names, scores


def dup_rows(a, indx, num_dups=1):
    """
    Duplicat rows in an np.array.
    :param a: np.array that should be enriched
    :param indx: index of a row that should be duplicated
    :param num_dups: number of duplicates that has to be inserted
    :return: np.array of the modified input a
    """
    return np.insert(a, [indx + 1] * num_dups, a[indx], axis=0)


def dup_cols(a, indx, num_dups=1):
    """
    Duplicat columns in an np.array.
    :param a: np.array that should be enriched
    :param indx: index of a column that should be duplicated
    :param num_dups: number of duplicates that has to be inserted
    :return: np.array of the modified input a
    """
    return np.insert(a, [indx + 1] * num_dups, a[:, [indx]], axis=1)


def enrich_input_table(table, names):
    """
    Enrich input table with more rows to make it square-shape.
    Where row names and column names are equal on the same indexes.
    :param table: input table
    :param names: input table names
    :return: np.array of enriched table names, np.array of enriched table
    """
    cols_rows_diff = table.shape[1] - table.shape[0]
    if cols_rows_diff > 0:
        for _ in range(cols_rows_diff):
            other_id = np.where(names == "Other")[0][0]
            table = dup_rows(table, other_id, cols_rows_diff)
            names = np.insert(names, other_id, "Other")
    return names, table


def enrich_adjacency_matrix(adjacency_matrix, adjacency_names, shapes_diff):
    """
    Enrich an adjacency matrix with more rows and columns to be the same shape as an input table.
    Where row names and column names are equal on the same indexes.
    :param adjacency_matrix: adjacency matrix indicators
    :param adjacency_names: adjacency matrix names
    :param shapes_diff: difference in shape comparing to the input table
    :return: np.array of enriched adjacency_matrix, np.array of enriched adjacency_names
    """
    other_id = np.where(np.array(adjacency_names) == "Other")[0][0]
    adjacency_matrix = dup_rows(adjacency_matrix, other_id, shapes_diff)
    adjacency_matrix = dup_cols(adjacency_matrix, other_id, shapes_diff)
    adjacency_names = np.insert(adjacency_names, other_id, "Other")
    return adjacency_matrix, adjacency_names


def form_adjacency_matrix(tab_names, adj_names, adj_matrix):
    """
    Formate adjacency matrix accordingly to the input table.
    :param tab_names: input table names
    :param adj_names: adjacency matrix names
    :param adj_matrix: adjacency table
    :return: np.array of final adjacency matrix
    """
    shapes_diff = len(tab_names) - len(adj_names)
    if shapes_diff > 0:
        adj_matrix, adj_names = enrich_adjacency_matrix(
            adj_matrix, adj_names, shapes_diff
        )

    indexes = []
    mat = []
    adj_mat_res = []

    # filter and rearrange rows
    for i in tab_names:
        index = np.where(adj_names == i)[0][0]
        indexes.append(index)
        mat.append(adj_matrix[index])

    k = 0
    for row in mat:
        adj_mat_res.append([])
        for index in indexes:
            adj_mat_res[k].append(row[index])
        k += 1

    # fill diagonal with ones
    adj_mat_res = np.array(adj_mat_res)
    np.fill_diagonal(adj_mat_res, 1)

    return adj_mat_res


def form_rules_matrix(tab_names, rules_names, rules_matrix):
    """
    Formate rules matrix accordingly to the input table.
    :param tab_names: input table names
    :param rules_names: rules matrix names
    :param rules_matrix: rules table
    :return: np.array of final rules matrix
    """
    shapes_diff = len(tab_names) - len(rules_names)
    if shapes_diff > 0:
        rules_matrix, rules_names = enrich_adjacency_matrix(
            rules_matrix, rules_names, shapes_diff
        )

    indexes = []
    mat = []
    rules_mat_res = []

    # select rows
    for i in tab_names:
        index = np.where(rules_names == i)[0][0]
        indexes.append(index)
        mat.append(rules_matrix[index])

    k = 0
    for row in mat:
        rules_mat_res.append([])
        for index in indexes:
            rules_mat_res[k].append(row[index])
        k += 1

    rules_mat_res = np.array(rules_mat_res)

    result = []
    for i in range(len(rules_mat_res)):
        result += np.where(rules_mat_res[i] == 1)

    return result


def permutations_optimised(iterable):
    pool = tuple(iterable)
    n = len(pool)
    indices = list(range(n))
    cycles = list(range(n, 0, -1))
    yield tuple(pool[i] for i in indices[:n])
    while n:
        for i in reversed(range(n)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:n])
                break
        else:
            return


def product(*args, with_trace=False):
    """
    Generating all possible combinations of column classes with the constraint -
    that one colum can be assigned to a class only once.
    :param args: adjacency matrix
    :param with_trace: should the trace be returned or not
    :return: generator with numpy array of arrays of combinations (branches)
    """
    pools = map(np.array, args)
    result = [[]]
    for i, pool in enumerate(pools):
        if with_trace:
            result = [
                x + [[j, i]]
                for x in result
                for j, _ in enumerate(pool)
                if not x or j not in np.array(x).T[0]
            ]
        else:
            result = [x + [j] for x in result for j, _ in enumerate(pool) if j not in x]

    for prod in result:
        yield np.array(prod)


def select_valid_branches(branches, rules_matrix, adjacency_matrix, with_trace=False):
    """
    Filtering out branches that does not meet the restrictions in Adjacency Matrix and Rules Matrix.
    :param branches: branches to check
    :param rules_matrix: rules matrix
    :param adjacency_matrix: adjacency matrix
    :param with_trace: True if input branches would have traces
    :return: np.array of selected branches
    """
    valid_branches = []
    for gid in range(len(branches)):
        valid = True
        if with_trace:
            trace = np.array(branches[gid])[:, 1]
            branch = np.array(branches[gid])[:, 0]
            branch_argsort = np.argsort(branch)

            for i in range(len(branch) - 1):
                if not adjacency_matrix[branch_argsort[i]][branch_argsort[i + 1]] == 1:
                    valid = False
                    break
        else:
            branch_argsort = np.argsort(branches[gid])

            for i in range(len(branches[gid]) - 1):
                # check if adjacency constrains are met
                if not adjacency_matrix[branch_argsort[i]][branch_argsort[i + 1]] == 1:
                    valid = False
                    break
                # check if rules constrains are meet
                if not all(
                    np.in1d(branch_argsort[i + 1 :], rules_matrix[branch_argsort[i]])
                ):
                    valid = False
                    break
        if valid:
            valid_branches.append(branches[gid])
    return np.array(valid_branches)


def get_branches_scores(branches, input_table, with_trace=False):
    """
    Calculate sum of scores for each branch.
    :param branches: branches
    :param input_table: input table
    :param with_trace: True if input branches would have traces
    :return: np.array with branches scores
    """
    branches_scores = []

    for branch in branches:
        pool = []
        if with_trace:
            for ind, edge in enumerate(np.array(branch)[:, 0]):
                pool.append(input_table[ind][edge])
        else:
            for ind, edge in enumerate(branch):
                pool.append(input_table[ind][edge])
        branches_scores.append(pool)

    return np.array(branches_scores)


def get_optimal_solution(branches_scores, branches, table_names):
    """
    Find optimal branch(es) with corresponding score(s)
    :param branches_scores: branches scores
    :param branches: branches
    :param table_names: table names
    :return: np.array of optimal branches names, np.array of optimal branches scores
    """
    scores_sum = np.sum(branches_scores, axis=1)
    optimal_branches_ids = np.where(scores_sum == max(scores_sum))
    optimal_branches = branches[optimal_branches_ids]
    optimal_branches_scores = branches_scores[optimal_branches_ids]

    optimal_branches_names = []
    scores = []

    for i, tree in enumerate(optimal_branches):
        optimal_branches_names.append([e for _, e in sorted(zip(tree, table_names))])
        scores.append(sum(optimal_branches_scores[i]))

    # remove duplicated combinations if any
    optimal_branches_names = np.unique(optimal_branches_names, axis=0)
    scores = np.unique(scores, axis=0)

    return optimal_branches_names, scores


def check_presence(vec, check):
    """
    Check if the values are part of a vector.
    :param vec: vector in which we are looking for values
    :param check: values we are looking for
    :return: True if all values are present, False otherwise
    """
    return all([i in vec for i in check])
