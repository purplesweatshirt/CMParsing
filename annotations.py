import cv2
import json
import bezier
import numpy as np
from math import inf
import matplotlib.pyplot as plt


def find_keypoints(lst):
    lst = set([(item[0], item[1]) for item in lst])
    upper, lower, left, right = [], [], [], []
    curr_upper, curr_lower, curr_l, curr_r = inf, 0, inf, 0
    for point in lst:
        # Upper
        if point[1] < curr_upper:
            curr_upper = point[1]
            upper = [point[0], point[1]]
        # Lower
        if point[1] > curr_lower:
            curr_lower = point[1]
            lower = [point[0], point[1]]
        # Left
        if point[0] < curr_l:
            curr_l = point[0]
            left = [point[0], point[1]]
        # Right
        if point[0] > curr_r:
            curr_r = point[0]
            right = [point[0], point[1]]
    if left[0] in [upper[0]] + [lower[0]]:
        return [upper] + [lower] + [right]
    else:
        return [upper] + [lower] + [left]


def get_bounding_box(node_obj, img_h):
    if node_obj['shape'] == 'plaintext':
        if not 'fill_color' in node_obj.keys():
            point = [float(coord) for coord in node_obj['pos'].split(',')]
            x, y = point[0], point[1]
            height = node_obj['_ldraw_'][0]['size']
            width = node_obj['_ldraw_'][2]['width']
            x, y, w, h = (4 / 3) * (x + 4), (4 / 3) * (y + 4), width, height
            x1, y1, x2, y2 = int(x - w), img_h - int(y - h), int(x + w), img_h - int(y + h)
        elif node_obj['fillcolor'] == '#FFFFFF':
            point = [float(coord) for coord in node_obj['pos'].split(',')]
            x, y = point[0], point[1]
            height = node_obj['_ldraw_'][0]['size']
            width = node_obj['_ldraw_'][2]['width']
            x, y, w, h = (4 / 3) * (x + 4), (4 / 3) * (y + 4), width, height
            x1, y1, x2, y2 = int(x - w), img_h - int(y - h), int(x + w), img_h - int(y + h)
        else:
            points = node_obj['_draw_'][-1]['points']
            xs, ys = [point[0] for point in points], [point[1] for point in points]
            x1, y1, x2, y2 = (4 / 3) * (min(xs) + 4), (4 / 3) * (min(ys) + 4), (4 / 3) * (max(xs) + 4), (4 / 3) * (
                        max(ys) + 4)
            x1, y1, x2, y2 = int(x1), img_h - int(y1), int(x2), img_h - int(y2)
        return x1, y1, x2, y2
    elif node_obj['shape'] in ['box', 'diamond', 'rectangle', 'square']:
        if node_obj['shape'] == 'box':
            points = node_obj['_draw_'][-1]['points']
        elif node_obj['shape'] in ['diamond', 'rectangle', 'square']:
            points = node_obj['_draw_'][-1]['points']
        xs, ys = [point[0] for point in points], [point[1] for point in points]
        x1, y1, x2, y2 = (4 / 3) * (min(xs) + 4), (4 / 3) * (min(ys) + 4), (4 / 3) * (max(xs) + 4), (4 / 3) * (
                    max(ys) + 4)
        return int(x1), img_h - int(y1), int(x2), img_h - int(y2)
    elif node_obj['shape'] in ['ellipse', 'doublecircle', 'circle', 'oval']:
        if node_obj['shape'] in ['ellipse', 'circle', 'oval']:
            points = node_obj['_draw_'][-1]['rect']
        elif node_obj['shape'] == 'doublecircle':
            points = node_obj['_draw_'][-1]['rect']
        x, y, w, h = (4 / 3) * (points[0] + 4), (4 / 3) * (points[1] + 4), (4 / 3) * (points[2]), (4 / 3) * (points[3])
        x1, y1, x2, y2 = int(x - w), img_h - int(y - h), int(x + w), img_h - int(y + h)
        return x1, y1, x2, y2


def eucl_dist2d(x, y):
    return ((y[0] - x[0]) ** 2 + (y[1] - x[1]) ** 2) ** 0.5


def find_arrow_end(arrow_points, line_point):
    curr_max, max_ind = 0, -1

    for i, p in enumerate(arrow_points):
        d = eucl_dist2d(p, line_point)
        if d >= curr_max:
            curr_max = d
            max_ind = i

    return arrow_points[max_ind]


def on_line(points):
    start, end = points[0], points[-1]
    line = [[(1 - t) * start[0] + t * end[0], (1 - t) * start[1] + t * end[1]]
            for t in np.linspace(0, 1, 100)
            ]

    points_on_line = []

    for p in points:
        for q in line:
            if eucl_dist2d(p, q) < 4:
                points_on_line.append(p)
                break

    return len(points_on_line) == len(points)


def check_invalid_nodes(node_obj):
    contains_invalid_node = False

    if not 'shape' in node_obj.keys():
        return True

    if node_obj['shape'] == 'plaintext':
        if 'fill_color' in node_obj.keys():
            if node_obj['fillcolor'] != '#FFFFFF':
                contains_invalid_node = True

    return contains_invalid_node


def generate_annotations(path2json, path2img, display=True):
    with open(path2json) as file:
        json_file = json.load(file)

    img = cv2.imread(path2img)
    img_name = path2img.split('/')[-1]
    an_name = img_name[:-3] + 'json'
    save_path = f"seg_annots/{an_name}"
    if 'splines' in json_file.keys():
        splines = json_file['splines']
    else:
        splines = 'spline'

    annots = {'image': img_name, 'masks': [], 'labels': [], 'bboxes': []}

    if ('circo' in path2img) or ('dot' in path2img):

        if not any([check_invalid_nodes(node) for node in json_file['objects']
                    if not 'cluster_' in node['name']]):

            print(path2img)
            print(save_path)
            helper = np.zeros((img.shape[0], img.shape[1]), np.uint8)

            # Nodes
            for node in json_file['objects']:
                if 'cluster_' in node['name']:
                    continue
                else:
                    node_name = node['label']
                    node_class = node['name'].split('_')[-1]
                    node_name = node['_ldraw_'][2]['text']
                    node_shape = node['shape']

                    x1, y1, x2, y2 = get_bounding_box(node, img.shape[0])
                    x1, x2 = min([x1, x2]), max([x1, x2])
                    y1, y2 = min([y1, y2]), max([y1, y2])
                    width, height = x2 - x1, y2 - y1

                    if node_shape in ['rectangle', 'square', 'plaintext', 'box']:
                        img = cv2.rectangle(img, [x1, y1], [x2, y2], (0, 255, 255), 2)
                        cv2.rectangle(helper, [x1, y1], [x2, y2], 255, 2)
                    elif node_shape in ['oval', 'ellipse', 'doublecircle', 'circle']:
                        x_center, y_center = (x1 + x2) // 2, (y1 + y2) // 2
                        w, h = width // 2, height // 2
                        cv2.ellipse(img, [x_center, y_center], [w, h],
                                    0, 0, 360, (0, 255, 255), 2)
                        cv2.ellipse(helper, [x_center, y_center], [w, h],
                                    0, 0, 360, 255, 2)

                    contours, hierarchy = cv2.findContours(helper, cv2.RETR_TREE,
                                                           cv2.CHAIN_APPROX_SIMPLE)
                    annots['masks'].append(contours[0].tolist())
                    annots['bboxes'].append([x1, y1, x2, y2])
                    annots['labels'].append('node')
                    helper[:, :] = 0

            # Edges
            for edge in json_file['edges']:

                points = edge['_draw_'][-1]['points']
                points_rescaled = [[int((4 / 3) * (point[0] + 4)),
                                    img.shape[0] - int((4 / 3) * (point[1] + 4))]
                                   for point in points]
                img = cv2.circle(img, [points_rescaled[0][0], points_rescaled[0][1]], 0,
                                 (128, 0, 255), thickness=7)
                img = cv2.circle(img, [points_rescaled[-1][0], points_rescaled[-1][1]], 0,
                                 (255, 128, 0), thickness=7)
                linewidth = 2
                bbox = []

                if 'style' in edge['_draw_'][0].keys():
                    lw = edge['_draw_'][0]['style']
                    if 'setlinewidth' in lw:
                        lw = lw.replace('setlinewidth', '')
                        linewidth = float(lw[1:-1]) + 1
                        linewidth = int(linewidth)
                        if linewidth < 2:
                            linewidth = 2

                # orthogonal and polyline edges
                if splines in ['polyline', 'ortho']:
                    # Connect each tuple by a straight line
                    for i in range(len(points_rescaled) - 1):
                        p1, p2 = points_rescaled[i], points_rescaled[i + 1]
                        img = cv2.line(img, p1, p2, color=(50, 0, 200),
                                       thickness=linewidth)
                        cv2.line(helper, p1, p2, color=(50, 0, 200),
                                 thickness=linewidth)
                        bbox.append(p1)
                        bbox.append(p2)

                # all other edge types
                elif splines in ['spline', 'curved']:
                    # Graphviz uses piecewise cubic bezier curves (4 points per segment)
                    spline_points = []
                    nodes_np = np.asfortranarray([[n[0] for n in points_rescaled],
                                                  [n[1] for n in points_rescaled]]
                                                 )
                    n = nodes_np.shape[1]
                    n_runs = n // 3
                    for i in range(n_runs):
                        # get 4 consecutive points
                        nodes_piece = nodes_np[:, 3 * i: 1 + (3 * (i + 1))]
                        curve = bezier.Curve(nodes_piece, degree=3)
                        # reconstruct bezier curve                        
                        pts = [[curve.evaluate(t).tolist()[0][0],
                                curve.evaluate(t).tolist()[1][0]]
                               for t in np.linspace(0, 1, 250)
                               ]
                        spline_points = spline_points + pts

                    pts_np = np.array(spline_points, np.int32)
                    img = cv2.polylines(img, [pts_np], isClosed=False,
                                        color=(200, 100, 50),
                                        thickness=linewidth)
                    cv2.polylines(helper, [pts_np], isClosed=False,
                                  color=(200, 100, 50), thickness=linewidth)
                    bbox = bbox + spline_points

                # arrow tip at the head
                backup = points_rescaled
                if '_hdraw_' in edge.keys():
                    points_hdraw = edge['_hdraw_'][-1]['points']
                    points_hdraw = [[int((4 / 3) * (point[0] + 4)),
                                     img.shape[0] - int((4 / 3) * (point[1] + 4))]
                                    for point in points_hdraw]
                    x1, x2, y1, y2 = [min([p[0] for p in points_hdraw]),
                                      max([p[0] for p in points_hdraw]),
                                      min([p[1] for p in points_hdraw]),
                                      max([p[1] for p in points_hdraw])]
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    line_end = [points_rescaled[-1][0], points_rescaled[-1][1]]
                    arrow_end = find_arrow_end(points_hdraw, line_end)
                    img = cv2.line(img, line_end, arrow_end, color=(200, 0, 50),
                                   thickness=linewidth)
                    cv2.line(helper, line_end, arrow_end, color=(200, 0, 50),
                             thickness=linewidth)
                    bbox.append([x1, y1])
                    bbox.append([x2, y2])
                    annots['masks'].append([x1, y1, x2, y2])
                    annots['bboxes'].append([x1, y1, x2, y2])
                    annots['labels'].append('arrow')

                # arrow tip at the tail
                if '_tdraw_' in edge.keys():
                    points_tdraw = edge['_tdraw_'][-1]['points']
                    points_tdraw = [[int((4 / 3) * (point[0] + 4)),
                                     img.shape[0] - int((4 / 3) * (point[1] + 4))]
                                    for point in points_tdraw]
                    x1, x2, y1, y2 = [min([p[0] for p in points_tdraw]),
                                      max([p[0] for p in points_tdraw]),
                                      min([p[1] for p in points_tdraw]),
                                      max([p[1] for p in points_tdraw])]

                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    line_start = [points_rescaled[0][0], points_rescaled[0][1]]
                    arrow_end = find_arrow_end(points_tdraw, line_start)
                    img = cv2.line(img, line_start, arrow_end,
                                   color=(200, 0, 50), thickness=linewidth)
                    cv2.line(helper, line_start, arrow_end, color=(200, 0, 50),
                             thickness=linewidth)
                    bbox.append([x1, y1])
                    bbox.append([x2, y2])
                    annots['masks'].append([x1, y1, x2, y2])
                    annots['bboxes'].append([x1, y1, x2, y2])
                    annots['labels'].append('arrow')

                contours, hierarchy = cv2.findContours(helper, cv2.RETR_TREE,
                                                       cv2.CHAIN_APPROX_SIMPLE)
                annots['masks'].append(contours[0].tolist())
                xs, ys = [p[0] for p in bbox], [p[1] for p in bbox]
                annots['bboxes'].append([min(xs), min(ys), max(xs), max(ys)])
                annots['labels'].append('edge')
                helper[:, :] = 0

                # edge weights
                if 'label' in edge.keys():
                    if edge['label']:
                        edge_weight = edge['_ldraw_'][-1]['text']
                        point = [float(coord) for coord in edge['lp'].split(',')]
                        x, y = int((4 / 3) * (point[0] + 4)), img.shape[0] - int((4 / 3) * (point[1] + 4))
                        for ind, dct in enumerate(edge['_ldraw_']):
                            if 'width' in dct.keys():
                                width_ind = ind
                            elif 'size' in dct.keys():
                                size_ind = ind
                        w = edge['_ldraw_'][width_ind]['width']
                        h = edge['_ldraw_'][size_ind]['size']
                        if " " in edge_weight:
                            x1, y1, x2, y2 = int(x - w), int(y - 2 * h), int(x + w), int(y + 2 * h)
                            img = cv2.rectangle(img, [x1, y1], [x2, y2],
                                                (0, 255, 255), 2)
                        else:
                            x1, y1, x2, y2 = int(x - w), int(y - h), int(x + w), int(y + h)
                            img = cv2.rectangle(img, [x1, y1], [x2, y2],
                                                (0, 255, 255), 2)

                        annots['masks'].append([x1, y1, x2, y2])
                        annots['bboxes'].append([x1, y1, x2, y2])
                        annots['labels'].append('weight')

            with open(save_path, "w") as fp:
                json.dump(annots, fp)
            # annot_file.close()

        if display:
            plt.figure(figsize=(20, 20))
            plt.imshow(img)
            plt.show()

