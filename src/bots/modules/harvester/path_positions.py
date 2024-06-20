from EzreD2Shared.shared.entities.position import Position
from EzreD2Shared.shared.utils.algos.tsp import greedy_algorithm, solve_tsp_dynamic
from EzreD2Shared.shared.utils.debugger import timeit
from EzreD2Shared.shared.utils.randomizer import multiply_offset


@timeit
def find_optimal_path_positions(
    positions: list[Position],
    start_pos: Position | None = None,
    end_pos: Position | None = None,
) -> tuple[float, list[Position]]:
    if start_pos is not None:
        positions.insert(0, start_pos)
    if end_pos is not None:
        positions.append(end_pos)

    total_dist: float

    if len(positions) <= 2:
        total_dist, optimal_path = 0, positions
    else:
        distance_matrix = [
            [x.get_distance(y) * multiply_offset() for y in positions]
            for x in positions
        ]
        total_dist, path = solve_tsp_dynamic(
            distance_matrix, start_pos is not None, end_pos is not None
        )
        optimal_path = [positions[index] for index in path]

    if start_pos is not None:
        optimal_path = optimal_path[1:]
    if end_pos is not None:
        optimal_path = optimal_path[:-1]
    return total_dist, optimal_path


@timeit
def find_dumby_optimal_path_positions(
    intermediate_pos: list[Position],
    start_pos: Position | None = None,
) -> list[Position]:
    if start_pos:
        intermediate_pos.insert(0, start_pos)

    path = greedy_algorithm(
        intermediate_pos,
        dist_func=lambda elem1, elem2: elem1.get_distance(elem2) * multiply_offset(),
    )
    if start_pos:
        path = path[1:]
    return path
