from rcd import l_marvel
from rcd.utilities.ci_tests import *
from rcd.utilities.data_graph_generation import *
from rcd.utilities.utils import f1_score_edges, compute_mb


def test_with_data():
    """
    Test L-Marvel on multiple random graphs with data and the Fisher Z test. We expect L-MARVEL to achieve a very
    high F1 score.
    """

    n = 20
    p = 1 / n

    num_graphs_to_test = 10
    np.random.seed(2308)
    for i in range(num_graphs_to_test):
        # generate a random Erdos-Renyi DAG
        adj_mat = gen_er_dag_adj_mat(n, p)

        # get graph clique number
        graph = nx.from_numpy_array(adj_mat, create_using=nx.DiGraph).to_undirected()

        # generate data from the DAG (unused as we use a perfect CI test)
        data_df = gen_gaussian_data(adj_mat, 50 * n)
        ci_test = lambda x, y, z, data: fisher_z(x, y, z, data, significance_level=1 / n ** 2)

        # run l-marvel
        learned_skeleton = l_marvel.learn_and_get_skeleton(ci_test, data_df)

        # compare the learned skeleton to the true skeleton
        true_skeleton = nx.from_numpy_array(adj_mat, create_using=nx.Graph)

        # compute F1 score
        precision, recall, f1_score = f1_score_edges(true_skeleton, learned_skeleton, return_only_f1=False)
        assert f1_score >= 0.94, "F1 score of " + str(f1_score) + " for graph " + str(i) + " should be 1!"
    print("L-MARVEL passed the second test!")


def test_with_perfect_ci():
    """
    Test on 100 random ER graphs with known clique numbers. We expect it to get a perfect F1 score with perfect CI tests.
    """
    n = 20
    p = 2 * np.log(n) / n

    num_graphs_to_test = 10
    np.random.seed(2308)
    for i in range(num_graphs_to_test):
        # generate a random Erdos-Renyi DAG
        adj_mat = gen_er_dag_adj_mat(n, p)

        # generate data from the DAG (unused as we use a perfect CI test)
        data_df = gen_gaussian_data(adj_mat, 1)

        ci_test = get_perfect_ci_test(adj_mat)
        find_markov_boundary_matrix_fun = lambda data: compute_mb(data, ci_test)
        learned_skeleton = l_marvel.learn_and_get_skeleton(ci_test, data_df, find_markov_boundary_matrix_fun)

        # compare the learned skeleton to the true skeleton
        true_skeleton = nx.from_numpy_array(adj_mat, create_using=nx.Graph)

        # compute F1 score
        precision, recall, f1_score = f1_score_edges(true_skeleton, learned_skeleton, return_only_f1=False)
        assert f1_score == 1, "F1 score of " + str(f1_score) + " for graph " + str(i) + " should be 1!"
    print("L-MARVEL passed the second test!")
