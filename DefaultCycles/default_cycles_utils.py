from DefaultCycles.environment import Environment

t = 15  # Cycle time threshold


def fixed_cycle_action(sim, dummy=None) -> bool:
    """ Returns a boolean indicating to take an action
    if the enough time elapsed since previous action """
    switch = False
    traffic_signal = sim.traffic_signals[0]
    time_elapsed = sim.t - traffic_signal.prev_update_time >= t
    if time_elapsed:
        traffic_signal.prev_update_time = sim.t
        switch = True
    return switch


def longest_queue_action(curr_state, prev_state) -> bool:
    """ Returns a boolean indicating to take an action
    if the enough time elapsed since previous action """
    switch = False
    traffic_signal = curr_state.traffic_signals[0]
    time_elapsed = curr_state.t - traffic_signal.prev_update_time >= t
    if time_elapsed:
        traffic_signal_state, n_direction_1_vehicles, n_direction_2_vehicles, non_empty_junction = prev_state
        # If the direction with most vehicles has a red light, switch it to green
        if traffic_signal_state and n_direction_1_vehicles < n_direction_2_vehicles:
            switch = True
        elif not traffic_signal_state and n_direction_1_vehicles > n_direction_2_vehicles:
            switch = True
    if switch:
        # Update the traffic signal update time
        traffic_signal.prev_update_time = curr_state.t
    return switch


q1_prev = None
q2_prev = None
MIN_GREEN = 10
MAX_GREEN = 20
SWITCH_THRESHOLD = 5 # predicted chênh lệch
def plqf_action(curr_state, prev_state) -> bool:
    """ PLQF: Prediction-based Longest Queue First scheduling.
    Uses queue growth to predict queue lengths and decides based on predicted congestion.
    """
    global q1_prev, q2_prev

    switch = False
    traffic_signal = curr_state.traffic_signals[0]
    inbound = traffic_signal.roads

    # Lấy q1, q2 hiện tại từ Simulation theo hai hướng
    q1_curr = sum(len(r.vehicles) for r in inbound[0])
    q2_curr = sum(len(r.vehicles) for r in inbound[1])
    
    if q1_prev is None:
        q1_prev = q1_curr
        q2_prev = q2_curr
        traffic_signal.prev_update_time = curr_state.t
        return longest_queue_action(curr_state, prev_state)

    dt = curr_state.t - traffic_signal.prev_update_time

    growth_q1 = (q1_curr - q1_prev) / max(dt, 1e-3)
    growth_q2 = (q2_curr - q2_prev) / max(dt, 1e-3)
    
    # # Predict queue
    # total_vehicles = q1_curr + q2_curr
    # if total_vehicles < 4:
    #     horizon = 0
    # elif total_vehicles < 7:
    #     horizon = 15
    # else:
    #     horizon = 25
    horizon = max(5, min(20, dt))

    predicted_q1 = q1_curr + growth_q1 * horizon
    predicted_q2 = q2_curr + growth_q2 * horizon
    diff = abs(predicted_q1 - predicted_q2)

    traffic_signal_state, _, _, _ = prev_state 

    # Decision logic based on predicted values
    if diff >= SWITCH_THRESHOLD:
        if traffic_signal_state and predicted_q2 > predicted_q1:
            switch = True
        elif not traffic_signal_state and predicted_q1 > predicted_q2:
            switch = True

    if dt >= MAX_GREEN:
        switch = True

    if switch and dt >= MIN_GREEN:
        traffic_signal.prev_update_time = curr_state.t

    q1_prev = q1_curr
    q2_prev = q2_curr

    return switch


action_funcs = {'fc': fixed_cycle_action,
                'lqf': longest_queue_action,
                'plqf': plqf_action}


def default_cycle(n_episodes: int, action_func_name: str, render):
    print(f"\n -- Running {action_func_name} for {n_episodes} episodes  -- ")
    environment: Environment = Environment()
    total_wait_time, total_collisions = 0, 0
    action_func = action_funcs[action_func_name]
    global q1_prev, q2_prev
    for episode in range(1, n_episodes + 1):
        q1_prev = None
        q2_prev = None
        state = environment.reset(render)
        score = 0
        collision_detected = 0
        done = False

        while not done:
            action = action_func(environment.sim, state)
            state, reward, done, truncated = environment.step(action)
            if truncated:
                exit()
            score += reward
            collision_detected += environment.sim.collision_detected

        if collision_detected:
            print(f"Episode {episode} - Collisions: {int(collision_detected)}")
            total_collisions += 1
        else:
            wait_time = environment.sim.current_average_wait_time
            total_wait_time += wait_time
            print(f"Episode {episode} - Wait time: {wait_time:.2f}")

    n_completed = n_episodes - total_collisions
    print(f"\n -- Results after {n_episodes} episodes: -- ")
    print(
        f"Average wait time per completed episode: {total_wait_time / n_completed:.2f}")
    print(f"Average collisions per episode: {total_collisions / n_episodes:.2f}")
