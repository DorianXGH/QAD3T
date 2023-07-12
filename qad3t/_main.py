import random
from pynput import keyboard
import sys
import time

import importlib.resources

with (importlib.resources.files("qad3t") / "dict.txt").open() as file:
    dic = file.read().split("\n")


def f_vector(word):
    vector = []
    for a in "abcdefghijklmnopqrstuvwxyz":
        vector.append(word.count(a) / len(word))
    return vector


enriched_dic = []
for word in dic:
    if word != "":
        enriched_dic.append([word, f_vector(word)])


def f_distance(v1, v2):
    distance = 0
    for i in range(len(v1)):
        distance += abs(v1[i] - v2[i])
    return distance ** (1 / 2)


geo_coef = 0.5


def probabilised(target_vector) -> list:
    sorted_dic = enriched_dic.copy()
    sorted_dic.sort(key=lambda x: f_distance(x[1], target_vector))
    probabilities = []
    for i in range(len(sorted_dic)):
        probabilities.append(((1 - geo_coef) ** i) * geo_coef)

    return (sorted_dic, probabilities)


def choose(target_vector, n):
    sorted_dic, probabilities = probabilised(target_vector)
    return random.choices(sorted_dic, weights=probabilities, k=n)


confusion_matrix = [[1 / (26 * 26) for i in range(26)] for j in range(26)]
tpc_vector = [1 for i in range(26)]

decay = 0.95
tpc_decay = 0.95


def decay_confusion_matrix():
    global confusion_matrix
    for i in range(len(confusion_matrix)):
        for j in range(len(confusion_matrix[i])):
            confusion_matrix[i][j] *= decay


def update_confusion_matrix(intended: chr, actual: chr):
    global confusion_matrix
    if (
        intended not in "abcdefghijklmnopqrstuvwxyz"
        or actual not in "abcdefghijklmnopqrstuvwxyz"
    ):
        return

    print("-------------------- ")
    print(intended)
    print(actual)
    print(ord(intended) - ord("a"))
    print(ord(actual) - ord("a"))
    print("-------------------- ")
    confusion_matrix[ord(intended) - ord("a")][ord(actual) - ord("a")] += 1


def generate_vector_from_matrix():
    global confusion_matrix
    vector = []
    for i in range(len(confusion_matrix)):
        total = 0
        for j in range(len(confusion_matrix[i])):
            total += confusion_matrix[i][j]
        vector.append(total)
    # normalise
    for i in range(len(vector)):
        vector[i] /= sum(vector)

    return vector


def normalised_tpc_vector():
    global tpc_vector
    ntpc_vec = tpc_vector.copy()
    total = sum(tpc_vector)
    for i in range(len(tpc_vector)):
        ntpc_vec[i] /= total
    return ntpc_vec


def update_tpc_vector(intended: chr, time: int):
    global tpc_vector
    if intended not in "abcdefghijklmnopqrstuvwxyz":
        return
    tpc_vector[ord(intended) - ord("a")] += (
        tpc_decay * tpc_vector[ord(intended) - ord("a")] + (1 - tpc_decay) * time
    )


def generate_target_vector():
    vtpc = normalised_tpc_vector()
    vcmx = generate_vector_from_matrix()
    v = [vtpc[i] + vcmx[i] for i in range(len(vtpc))]
    print(v)
    return v


def gen_target_string(n=10):
    target_string = ""
    choices = choose(generate_target_vector(), n)
    c_strs = [c[0] for c in choices]
    target_string = " ".join(c_strs)
    return target_string.lower()


def get_wpm():
    # tpc : time per character
    global tpc_vector
    average_tpc = sum(tpc_vector) / len(tpc_vector)
    average_tps_s = average_tpc / 1000000000
    return 60 * 5 / average_tps_s


tgt_str = gen_target_string()
time_c = time.time_ns()
print(tgt_str)


def on_press(key):
    global tgt_str
    global time_c
    try:
        pressed = ""
        if key == keyboard.Key.space:
            pressed = " "
        else:
            pressed = key.char
        if pressed == tgt_str[0]:
            tgt_str = tgt_str[1:]
            n_time = time.time_ns()
            update_tpc_vector(pressed, n_time - time_c)
            time_c = n_time
            if tgt_str == "":
                tgt_str = gen_target_string()
        else:
            if pressed != " ":
                update_confusion_matrix(tgt_str[0], pressed)
        # print(chr(27) + "[2J")
        # print and go back to start of line
        print(" " + tgt_str + (" " * 10) + " WPM : " + str(get_wpm()), end="\r")

    except AttributeError:
        if key == keyboard.Key.enter:
            tgt_str = gen_target_string()
        if key == keyboard.Key.esc:
            return False
        print("special key {0} pressed".format(key))


def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False


# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

input_text = sys.stdin.read()
