import argparse
import xmltodict
import json
import math
import os
from scipy.stats import beta
import numpy as np
import itertools


attr_keys = ["TILT", "LEFT_DIFFERENTIAL", "RIGHT_DIFFERENTIAL"]
attr_data = [[]] * len(attr_keys)


def calculate_distance(x1, y1, z1, x2, y2, z2):
    return ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**(1/2)

def calculate_2d_distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**(1/2)

def compute_tilt_interval(tilt_data):
    a, b, loc, scale = beta.fit(tilt_data)

    cis = beta.interval(0.95, a, b, loc, scale)
    return cis[1]


def preprocess(dir, out_fp, hz=1, slip=False, n=None, sim_ids=None):

    # Waypoints
    rseq_fp = './{}/input.rseq'.format(dir)

    # Parse for waypoints in the input sequence
    cx = []
    cy = []
    r = []
    waypoints = []
    with open(rseq_fp, 'r') as rseq:
        txt_lines = rseq.readlines()

        cx = [t.split(' ')[1] for t in txt_lines if 'MOB_SET_NAV_GOAL' in t]
        cy = [t.split(' ')[2] for t in txt_lines if 'MOB_SET_NAV_GOAL' in t]
        r = [t.split(' ')[1]
             for t in txt_lines if 'MOB_GO_TO' in t]

        waypoints = [{'cx': wp[0], 'cy': wp[1], 'r': wp[2]}
                     for wp in zip(cx, cy, r)]

        with open('./public/{}/wp.json'.format(out_fp), 'w') as outfile:
            json.dump(waypoints, outfile)

    # rksml files
    # with open('./{}/dir.txt'.format(dir)) as f:
    from os import listdir
    from os.path import isfile, join
    sim_ids = [f for f in listdir('./{}/'.format(dir)) if not isfile(join('./{}/'.format(dir), f))]

    
        # if sim_ids == None:
        #     sim_ids = f.read().splitlines()
    # sim_ids = onlyfiles

    summary = []
    history = []

    desired_data = ["QUAT_X", "QUAT_Y", "QUAT_Z", "QUAT_C", "ROVER_X", "ROVER_Y", "ROVER_Z"]

    for sim_id in sim_ids[:n]:
        print(sim_id)
        try:
            sim_id = sim_id.split('/')[0]
            int(sim_id)
        except ValueError:
            continue
    
        slip_fp = './{}/{}/ssim_cmd.txt'.format(dir, sim_id)
        log_fp = './{}/{}/ssim_evrs.log'.format(dir, sim_id)
        history_fp = './{}/{}/mob_motion_history.rksml'.format(dir, sim_id)

        # Look for the failure flag in this simulation log
        failure = True
        failure_time = -1.0
        failure_flag = 'MOB_GOAL_ERROR=TRUE'
        with open(log_fp, 'r') as log_file:
            txt_lines = log_file.readlines()
            filtered_lines = [t for t in txt_lines if failure_flag in t]
            failure = bool(len(filtered_lines))
            if failure:
                failure_time = float(filtered_lines[0].split(' ')[1])
        failure_loc = {}

        # When were the waypoints reached?
        wp_reached = []
        reached_flag = 'NAV_EVR_ACTION_GO_TO_DIRECTIVE_GOAL_REACHED_WAITING_FOR_OTHER_STEPS'
        with open(log_fp, 'r') as log_file:
            txt_lines = log_file.readlines()
            wp_reached = [float(t.split(' ')[1])
                            for t in txt_lines if reached_flag in t]
        wp_history = [{}] * len(waypoints)

        # History
        xmlDict = xmltodict.parse(open(history_fp, "r").read())
        state_history = xmlDict['RPK_Set']['State_History']['Node']

        sim_history = []
        state_dict = {}
        last_time = -1.0
        total_distance = 0
        total_2d_distance = 0
        last_point = {'ROVER_X': 0.0, 'ROVER_Y':0.0, 'ROVER_Z': 0.0}

        for i, state in enumerate(state_history[::(hz*8)]):
            knot = state['Knot']
            state_dict = dict((v['@Name'], float(v['#text']))
                                for v in knot if v['@Name'] in desired_data)

            state_dict["ROLL"], state_dict["PITCH"], state_dict["YAW"] = euler_from_quaternion(
                state_dict["QUAT_X"],
                state_dict["QUAT_Y"],
                state_dict["QUAT_Z"],
                state_dict["QUAT_C"]
            )

            state_dict["TILT"] = abs(state_dict["ROLL"]) + abs(state_dict["PITCH"])

            current_distance = calculate_distance(
                last_point['ROVER_X'], last_point['ROVER_Y'], last_point['ROVER_Z'],
                state_dict['ROVER_X'], state_dict['ROVER_Y'], state_dict['ROVER_Z'],
            )
            # current_2d_distance = calculate_2d_distance(
            #     last_point['ROVER_X'], last_point['ROVER_Y'],
            #     state_dict['ROVER_X'], state_dict['ROVER_Y']
            # )
            total_distance += current_distance
            # total_2d_distance += current_2d_distance
            state_dict["DISTANCE"] = current_distance
            # state_dict["2DISTANCE"] = current_2d_distance
            last_point = state_dict

            state_dict['@Time'] = i * hz

            for j, reached in enumerate(wp_reached):
                if last_time <= reached and reached <= float(state['@Time']):
                    wp_history[j] = {
                        'cx': state_dict["ROVER_X"], 
                        'cy': state_dict["ROVER_Y"],
                        't': i * hz
                        # 'dist': total_2d_distance
                    }

            last_time = float(state['@Time'])
            state_dict['simId'] = sim_id

            for i, key in enumerate(attr_keys):
                if key in state_dict:
                    attr_data[i].append(state_dict[key]) 

            sim_history.append(state_dict)
        
        # if not failure:
        #     wp_history[-1] = {
        #         'cx': state_dict["ROVER_X"], 
        #         'cy': state_dict["ROVER_Y"],
        #         't': i * hz,
        #         'dist': total_2d_distance
        #     }

        #     wp_starts = [0] + [wp['t'] + 1 for wp in wp_history[:-1]]
        #     wp_start_dists = [0] + [wp['dist'] + 1 for wp in wp_history[:-1]]
        #     for i, wp in enumerate(wp_history):
        #         dist_interval = 0.05 * (wp['dist']-wp_start_dists[i])
        #         total_wp_distance = 0

        #         curve = []
        #         for prev_id, point in enumerate(sim_history[wp_starts[i]:wp_history[i]['t']]):
        #             current_wp_distance = point['2DISTANCE']
        #             if total_wp_distance + current_wp_distance > dist_interval:
        #                 curve.append([point['ROVER_X'], point['ROVER_Y']])
        #                 total_wp_distance = dist_interval - total_wp_distance + current_wp_distance
        #             else:
        #                 total_wp_distance += current_wp_distance

        #         wp['arcLengthHistory'] = curve

        history.append({
            'simId': sim_id,
            'wpHistory': wp_history,
            'history': sim_history
        })

        # Parse for input slip value in the SSIM command
        slip_factor = None
        if slip:
            with open(slip_fp, 'r') as ssim_cmd:
                txt_lines = ssim_cmd.readlines()
                slip_factor = float(
                    [t for t in txt_lines if 'slip-factor' in t][0].split('=')[1])

        summary.append(
            {
                'simId': sim_id,
                'slip': slip_factor or 0.0,
                'failure': failure,
                'failureTime': failure_time,
                'distance': total_distance,
                'time': state_dict['@Time']
            }
        )
    
    ensemble = {
        'tiltUpper': compute_tilt_interval(attr_data[attr_keys.index("TILT")])
    }

    for i, key in enumerate(attr_keys):
        ensemble[key] = [min(attr_data[i]), max(attr_data[i])]

    with open('./public/{}/ensemble.json'.format(out_fp), 'w') as outfile:
        json.dump(ensemble, outfile)

    with open('./public/{}/summary.json'.format(out_fp), 'w') as outfile:
        json.dump(summary, outfile)

    with open('./public/{}/history.json'.format(out_fp), 'w') as outfile:
        json.dump(history, outfile)




def forward_fill_arr(arrs):
    arr = arrs
    mask = np.isnan(arr)
    idx = np.where(~mask,np.arange(mask.shape[1]),0)
    np.maximum.accumulate(idx,axis=1, out=idx)
    out = arr[np.arange(idx.shape[0])[:,None], idx]
    return out
        

def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in degrees (counterclockwise)
    pitch is rotation around y in degrees (counterclockwise)
    yaw is rotation around z in degrees (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.degrees(math.atan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.degrees(math.asin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.degrees(math.atan2(t3, t4))

    return roll_x, pitch_y, yaw_z


def q_conjugate(q):
    """
    conjugate the quaternion
    :param q: the quaternion
    """

    x, y, z, w = q
    return (-x, -y, -z, w)


def q_mult(q1, q2):
    """
    multiply two quaternions
    :param q1: quat 1
    :param q2: quat 2
    """

    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return x, y, z, w


def qv_mult(q1, v1):
    """
    rotate a vector by a quaternion
    :param q1: the quaternion
    :param v1: the vector
    """

    q2 = tuple(v1) + (0.0,)
    return q_mult(q_mult(q1, q2), q_conjugate(q1))[:3]


def get_wheel_data(data):
    """
    Get wheel position data. This allows us to define the bounds
    of the rover path plots
    :param data: data relevent to wheel position
    """

    # Distance from center of rover to wheels
    rover_half_width = 1.185

    # Array of wheel locations for all simulations
    wheels = [None] * len(data)

    for i, sim in enumerate(data):
        breakpoint()
        # Use position, orientation, and rover width to get wheel positions
        x = [state['ROVER_X'] for state in sim]
        y = [state['ROVER_Y'] for state in sim]
        wheel_right = [
            qv_mult([state["QUAT_X"], state["QUAT_Y"], state["QUAT_Z"], state["QUAT_C"]], [0, rover_half_width, 0]) for state in sim
        ]
        wheel_left = [
            qv_mult([state["QUAT_X"], state["QUAT_Y"], state["QUAT_Z"], state["QUAT_C"]], [0, -rover_half_width, 0]) for state in sim
        ]
        wheels[i] = [[v[0] + x, v[1] + y]
                     for x, y, v in zip(x, y, wheel_right)]
        wheels[i] += [[v[0] + x, v[1] + y]
                      for x, y, v in zip(x, y, wheel_left)]

    return wheels


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transform raw rksml files for GRIT.')
    parser.add_argument('--dir', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--slip', type=bool, required=False)

    args = parser.parse_args()

    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir('./{}/'.format(args.dir)) if isfile(join('./{}/'.format(args.dir), f))]
    cfa = ''
    dem = ''
    for fn in files:
        if 'cfa' in fn and ".pgm" in fn:
            if '.aux' in fn or '.xml' in fn:
                continue
            cfa = fn
    for fn in files:
        if 'dem' + cfa[3:].split('.')[0] in fn and ".pgm" in fn:
            if '.aux' in fn or '.xml' in fn:
                continue
            dem = fn

    # os.system("cd " + args.dir + " ls -d */ >> dir.txt && cd ..")
    os.system("cd public && mkdir " + args.output)

    # os.system("cd public && cp ../" + args.dir + "/" + cfa + " ./" + args.output + "/")
    # os.system("cd public && cp ../" + args.dir + "/" + dem + " ./" + args.output + "/")
    os.system("cd public && cp ../" + args.dir + "/*.pgm ./" + args.output + "/")

    # preprocess(args.dir, args.output, hz=1, sim_ids=["18693000","48056573","51706749","54349339","58273557","94646617","80785928","67737923"])
    preprocess(args.dir, args.output, hz=1, slip=args.slip)
