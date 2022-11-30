import os
import random
import graphviz
import itertools
import setup_config as scfg
from annotations import generate_annotations


class SEMGenerator:

    def __init__(self, output_path, json_path, latent_variables, observed_variables, item_edges=False):
        self.output_path = output_path
        self.json_path = json_path
        self.latent_variables = [lv if lv[-1].isalpha() else lv[:-1] for lv in latent_variables]
        self.obs_vars = observed_variables
        self.amount_obs_vars = [len(ovs) for ovs in self.obs_vars]
        self.n2 = len(list(itertools.combinations(self.latent_variables, 2)))
        self.n1 = len(self.latent_variables)
        # self.lv_edges = self._edge_directions(random.sample(list(itertools.combinations(self.latent_variables, 2)), random.randint(self.n1//2, self.n2-1))) if self.n2 > 2 else self._edge_directions([[self.latent_variables[0], self.latent_variables[1]]])
        if len(latent_variables) >= 2:
            self.lv_edges = self._edge_directions()
        else:
            self.lv_edges = []
        self.item_edges = item_edges
        self.words = scfg.WORDS.split()
        if self.item_edges:
            self.ov_edges = []
            self.m2 = len(list(itertools.combinations(self.obs_vars, 2)))
            self.m1 = sum(self.amount_obs_vars)
            item_cluster = random.choice(self.obs_vars)
            if len(item_cluster) > 0:
                item = random.choice(item_cluster)
                edge_cluster = random.choice(self.obs_vars)
                if edge_cluster == item_cluster:
                    edge_cluster = random.choice(self.obs_vars)
                self.ov_edges = [(item, other_item) for other_item in edge_cluster]

    def generate_custom(self, n):

        N = self.n1 + sum(self.amount_obs_vars)

        for l in range(n):
            arrow = random.choice(scfg.ARROW_SHAPE)
            edges_shape = random.choice(scfg.EDGE_ATTR)
            width = random.choice(scfg.PENWIDTHS)
            arrow_sz = random.choice(scfg.ARROWSIZES)
            arrow_style = random.choice(scfg.STYLES)
            pc_sz = random.choice(scfg.PC_FONTSIZES)
            items = random.choice(scfg.ITEM_SHAPE)
            lv_shapes = random.choice(scfg.LV_SHAPE)
            fill_color = random.choice(scfg.COLORS) + ':' + random.choice(
                scfg.COLORS) if random.random() < 0.2 else '#FFFFFF'
            fill_angle = str(random.randint(0, 360))
            error = random.choice(scfg.ERRORS)
            error_shape = random.choice(scfg.ERROR_SHAPE)
            fontname = random.choice(scfg.FONTNAMES)
            label_pos = random.choice(scfg.LABEL_POS)

            self.dot = graphviz.Digraph(comment=f'SEM_{l}', format='png', graph_attr={'splines': edges_shape},
                                        engine='neato')

            occupied = []

            for ind, lv in enumerate(self.latent_variables):

                self.dot.attr('node', shape=lv_shapes)
                pos_x, pos_y = random.randint(-N, N), random.randint(-N, N)

                while (pos_x, pos_y) in occupied:
                    pos_x, pos_y = random.randint(-N, N), random.randint(-N, N)

                occupied.append((pos_x, pos_y));
                occupied.append((pos_x + 1, pos_y));
                occupied.append((pos_x - 1, pos_y))
                occupied.append((pos_x, pos_y - 1));
                occupied.append((pos_x, pos_y + 1));
                occupied.append((pos_x + 1, pos_y + 1))
                occupied.append((pos_x - 1, pos_y + 1));
                occupied.append((pos_x + 1, pos_y - 1));
                occupied.append((pos_x - 1, pos_y - 1))

                pos = f'{pos_x},{pos_y}!'

                if len(lv) > 21:
                    fontsz = "8"
                elif len(lv) > 15:
                    fontsz = "10"
                elif len(lv) > 8:
                    fontsz = "12"
                else:
                    fontsz = "14"

                self.dot.node(f'{lv}_construct', lv, pos=pos, style='filled', fillcolor=fill_color,
                              gradientangle=fill_angle, fontname=fontname, fontsize=fontsz)

                for ov in self.obs_vars[ind]:

                    self.dot.attr('node', shape=items)

                    pos_x, pos_y = random.randint(-N // 2, N // 2), random.randint(-N // 2, N // 2)

                    while (pos_x, pos_y) in occupied:
                        pos_x, pos_y = random.randint(-N // 2, N // 2), random.randint(-N // 2, N // 2)

                    occupied.append((pos_x, pos_y));
                    occupied.append((pos_x + 1, pos_y));
                    occupied.append((pos_x - 1, pos_y))
                    occupied.append((pos_x, pos_y - 1));
                    occupied.append((pos_x, pos_y + 1));
                    occupied.append((pos_x + 1, pos_y + 1))
                    occupied.append((pos_x - 1, pos_y + 1));
                    occupied.append((pos_x + 1, pos_y - 1));
                    occupied.append((pos_x - 1, pos_y - 1))

                    pos = f'{pos_x},{pos_y}!'

                    if len(ov) > 21:
                        fontsz = "8"
                    elif len(ov) > 15:
                        fontsz = "10"
                    elif len(ov) > 8:
                        fontsz = "12"
                    else:
                        fontsz = "14"

                    self.dot.node(f'{ov}_item', ov, pos=pos, style='filled', fillcolor=fill_color,
                                  gradientangle=fill_angle, fontname=fontname, fontsize=fontsz)

                    if random.random() >= 0.1:
                        self.dot.edge(f'{lv}_construct', f'{ov}_item', label=self._create_edge_label(), fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)
                    else:
                        self.dot.edge(f'{lv}_construct', f'{ov}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)

            print("Generating edges")
            for edges in self.lv_edges:
                # direction = random.random()
                if random.random() >= 0.1:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  label=self._create_edge_label(), fontsize=pc_sz,
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname)
                else:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname)

            if self.item_edges:
                for edges in self.ov_edges:
                    if random.random() >= 0.1:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item', label=self._create_edge_label(),
                                      fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)
                    else:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)

            if random.random() >= 0.7:

                # Generate some random text 
                str1 = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                str2 = f"{random.choice(self.words)} {random.choice(self.words)} 9.021*** 0.8*"
                str3 = f"-0.34**, 0.87*** "
                str4 = f"-0.24**, {random.choice(self.words)} 0.17***"
                str5 = f"-0.912**, {random.choice(self.words)} 0.1319*** {random.choice(self.words)}"
                str6 = f"{random.choice(self.words)} -1.526**, {random.choice(self.words)} 0.187 {random.choice(self.words)}"
                str7 = f"{random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
                str8 = f"   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
                str9 = f"{random.choice(self.words)}   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
                str10 = f"{random.choice(self.words)}"
                str11 = f"{random.choice(self.words)}        {random.choice(self.words)}"
                random_list = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11]
                fontsize = str(random.choice([8, 12, 16, 20, 22]))

                if random.random() >= 0.9:
                    self.dot.attr(label=f'\n\n{random.choice(random_list)}', fontsize=fontsize, labelloc=label_pos[0],
                                  labeljust=label_pos[1])
                elif random.random() >= 0.8:
                    self.dot.attr(label=f'\n\n{random.choice(random_list)}\n{random.choice(random_list)}',
                                  fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
                elif random.random() >= 0.65:
                    self.dot.attr(
                        label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}',
                        fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
                elif random.random() >= 0.5:
                    self.dot.attr(
                        label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)} {random.choice(random_list)}',
                        fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])

            print(f'{self.output_path}_{edges}_{l}_custom.json')
            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_custom.json', format='json'))
            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_custom.png', format='png'))
            # Delete unnecessary files
            os.remove(f'{self.output_path}_{edges_shape}_{l}_custom.json')
            os.remove(f'{self.output_path}_{edges_shape}_{l}_custom.png')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_custom.json.json',
                      f'{self.output_path}_{edges_shape}_{l}_custom.json')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_custom.png.png',
                      f'{self.output_path}_{edges_shape}_{l}_custom.png')
            # Generate annotation files
            generate_annotations(f'{self.output_path}_{edges_shape}_{l}_custom.json',
                                 f'{self.output_path}_{edges_shape}_{l}_custom.png')

    def generate_random(self, n):

        n_vars = len(self.latent_variables)  # + sum(self.amount_obs_vars) // 2
        lv_positions = [f'{random.randint(-n_vars, n_vars)},{random.randint(-n_vars, n_vars)}!' for _ in
                        self.latent_variables]
        ov_positions = [
            [f'{random.randint(-n_vars, n_vars)},{random.randint(-n_vars, n_vars)}!' for _ in self.obs_vars[i]] for i in
            range(len(self.obs_vars))]

        for l in range(n):
            arrow = random.choice(scfg.ARROW_SHAPE)
            edges = random.choice(scfg.EDGE_ATTR[:-2])
            width = random.choice(scfg.PENWIDTHS)
            arrow_sz = random.choice(scfg.ARROWSIZES)
            arrow_style = random.choice(scfg.STYLES)
            pc_sz = random.choice(scfg.PC_FONTSIZES)
            items = random.choice(scfg.ITEM_SHAPE)
            lv_shapes = random.choice(scfg.LV_SHAPE)
            fill_color = random.choice(scfg.COLORS) + ':' + random.choice(
                scfg.COLORS) if random.random() < 0.5 else '#FFFFFF'
            fill_angle = str(random.randint(0, 360))
            error = random.choice(scfg.ERRORS)
            error_shape = random.choice(scfg.ERROR_SHAPE)
            fontname = random.choice(scfg.FONTNAMES)

            self.dot = graphviz.Digraph(comment=f'SEM_{l}', format='png', graph_attr={'splines': edges}, engine='neato')

            curr_h_pos = 0
            for ind, lv in enumerate(self.latent_variables):
                self.dot.attr('node', shape=lv_shapes)

                if len(lv) > 21:
                    fontsz = "8"
                elif len(lv) > 15:
                    fontsz = "10"
                elif len(lv) > 8:
                    fontsz = "12"
                else:
                    fontsz = "14"

                self.dot.node(f'{lv}_construct', lv, pos=lv_positions[ind], style='filled', fillcolor=fill_color,
                              gradientangle=fill_angle, fontname=fontname, fontsize=fontsz)

                self.dot.attr('node', shape=items)
                for j, ov in enumerate(self.obs_vars[ind]):

                    if len(lv) > 21:
                        fontsz = "8"
                    elif len(lv) > 15:
                        fontsz = "10"
                    elif len(lv) > 8:
                        fontsz = "12"
                    else:
                        fontsz = "14"

                    self.dot.node(f'{ov}_item', ov, style='filled', pos=ov_positions[ind][j], fillcolor=fill_color,
                                  gradientangle=fill_angle, fontname=fontname, fontsize=fontsz)
                    if random.random() >= 0.2:
                        self.dot.edge(f'{lv}_construct', f'{ov}_item', label=self._create_edge_label(), fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)
                    else:
                        self.dot.edge(f'{lv}_construct', f'{ov}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)
                    if (error_shape in ['circle', 'plaintext']) and (error != 'none'):
                        x, y = int(ov_positions[ind][j].split(',')[0]), int(ov_positions[ind][j].split(',')[1][:-1])
                        err_pos = f'{x + random.randint(-3, 3)},{y + random.randint(-3, 3)}!'
                        e_name = f'e{curr_h_pos}'
                        self.dot.node(f'{e_name}_error', e_name, pos=err_pos, shape=error_shape, style='filled',
                                      fillcolor=fill_color, gradientangle=fill_angle, fontname=fontname)
                        if random.random() >= 0.1:
                            self.dot.edge(f'{e_name}_error', f'{ov}_item', label='1  ', fontsize=pc_sz, arrowhead=arrow,
                                          arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                        else:
                            self.dot.edge(f'{e_name}_error', f'{ov}_item', arrowhead=arrow,
                                          arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)

                    elif (error_shape == 'self-loops') and (error != 'none'):
                        label = self._create_edge_label()
                        self.dot.edge(f'{ov}_item', f'{ov}_item', label=label, fontsize=pc_sz, arrowhead=arrow,
                                      arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)

                    curr_h_pos += 1

            for edges in self.lv_edges:
                if random.random() >= 0.1:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  label=self._create_edge_label(), fontsize=pc_sz,
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname)
                else:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname)

            if self.item_edges:
                for edges in self.ov_edges:
                    if random.random() >= 0.1:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item', label=self._create_edge_label(),
                                      fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)
                    else:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)

            # Generate some random text 
            str1 = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
            str2 = f"{random.choice(self.words)} {random.choice(self.words)} 9.021*** 0.8*"
            str3 = f"-0.34**, 0.87*** "
            str4 = f"-0.24**, {random.choice(self.words)} 0.17***"
            str5 = f"-0.912**, {random.choice(self.words)} 0.1319*** {random.choice(self.words)}"
            str6 = f"{random.choice(self.words)} -1.526**, {random.choice(self.words)} 0.187 {random.choice(self.words)}"
            str7 = f"{random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str8 = f"   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str9 = f"{random.choice(self.words)}   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str10 = f"{random.choice(self.words)}"
            str11 = f"{random.choice(self.words)}        {random.choice(self.words)}"
            random_list = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11]
            fontsize = str(random.choice([8, 12, 16, 20, 22]))
            if random.random() >= 0.85:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}', fontsize=fontsize)
            elif random.random() >= 0.5:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}\n{random.choice(random_list)}',
                              fontsize=fontsize)
            else:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}',
                    fontsize=fontsize)
            # print(self.dot.render(f'{self.json_path}_{l}_random', outfile=f'{self.output_path}_{l}_random.json'))
            # print(self.dot.render(f'{self.json_path}_{l}_random', outfile=f'{self.output_path}_{l}_random.png'))

    def generate_circo(self, n):

        for l in range(n):
            arrow = random.choice(scfg.ARROW_SHAPE)
            edges_shape = random.choice(scfg.EDGE_ATTR[:-2])
            width = random.choice(scfg.PENWIDTHS)
            arrow_sz = random.choice(scfg.ARROWSIZES)
            arrow_style = random.choice(scfg.STYLES)
            pc_sz = random.choice(scfg.PC_FONTSIZES)
            items = random.choice(scfg.ITEM_SHAPE)
            lv_shapes = random.choice(scfg.LV_SHAPE)
            fill_color = random.choice(scfg.COLORS) + ':' + random.choice(
                scfg.COLORS) if random.random() < 0 else '#FFFFFF'
            edge_color = random.choice(scfg.COLORS) if random.random() < 0.2 else '#000000'
            fill_angle = str(random.randint(0, 360))
            error = random.choice(scfg.ERRORS)
            error_shape = random.choice(scfg.ERROR_SHAPE)
            cluster = True if random.random() < 0.2 else False
            fontname = random.choice(scfg.FONTNAMES)
            label_pos = random.choice(scfg.LABEL_POS)

            self.dot = graphviz.Digraph(comment=f'SEM_{l}', format='png', graph_attr={'splines': edges_shape},
                                        engine='circo')

            curr_h_pos = 0
            for ind, lv in enumerate(self.latent_variables):
                if cluster and (random.random() < 0.33):

                    with self.dot.subgraph(name=f'cluster_{lv}') as c:
                        cluster_color = random.choice(scfg.COLORS) if random.random() < 0.5 else '#FFFFFF'
                        if cluster_color != '#FFFFFF':
                            c.attr(style='filled', color=cluster_color)
                        else:
                            c.attr(color=random.choice(scfg.COLORS))
                        c.attr('node', shape=lv_shapes)

                        if len(lv) > 21:
                            fontsz = "8"
                        elif len(lv) > 15:
                            fontsz = "10"
                        elif len(lv) > 8:
                            fontsz = "12"
                        else:
                            fontsz = "14"

                        c.node(f'{lv}_construct', lv, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                               fontname=fontname, fontsize=fontsz)

                        c.attr('node', shape=items)
                        for ov in self.obs_vars[ind]:

                            c.node(f'{ov}_item', ov, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                   fontname=fontname)
                            if random.random() >= 0.2:
                                c.edge(f'{lv}_construct', f'{ov}_item', label=self._create_edge_label(), fontsize=pc_sz,
                                       arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                       penwidth=width, fontname=fontname, color=edge_color)
                            else:
                                c.edge(f'{lv}_construct', f'{ov}_item',
                                       arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                       penwidth=width, fontname=fontname, color=edge_color)
                            if (error_shape in ['circle', 'plaintext']) and (error != 'none'):
                                e_name = f'e{curr_h_pos}'

                                c.node(f'{e_name}_error', e_name, shape=error_shape, style='filled',
                                       fillcolor=fill_color, gradientangle=fill_angle, fontname=fontname)
                                if random.random() >= 0.1:
                                    c.edge(f'{e_name}_error', f'{ov}_item', label='1  ', fontsize=pc_sz,
                                           arrowhead=arrow,
                                           arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                                else:
                                    c.edge(f'{e_name}_error', f'{ov}_item', arrowhead=arrow,
                                           arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)

                            elif (error_shape == 'self-loops') and (error != 'none'):
                                label = self._create_edge_label()
                                c.edge(f'{ov}_item', f'{ov}_item', label=label, fontsize=pc_sz, arrowhead=arrow,
                                       arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                            curr_h_pos += 1


                else:
                    self.dot.attr('node', shape=lv_shapes)

                    if len(lv) > 21:
                        fontsz = "8"
                    elif len(lv) > 15:
                        fontsz = "10"
                    elif len(lv) > 8:
                        fontsz = "12"
                    else:
                        fontsz = "14"

                    self.dot.node(f'{lv}_construct', lv, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                  fontname=fontname, fontsize=fontsz)

                    self.dot.attr('node', shape=items)
                    for ov in self.obs_vars[ind]:
                        self.dot.node(f'{ov}_item', ov, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                      fontname=fontname)
                        if random.random() >= 0.2:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item', label=self._create_edge_label(),
                                          fontsize=pc_sz,
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                        else:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item',
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                        if (error_shape in ['circle', 'plaintext']) and (error != 'none'):
                            e_name = f'e{curr_h_pos}'
                            self.dot.node(f'{e_name}_error', e_name, shape=error_shape, style='filled',
                                          fillcolor=fill_color, gradientangle=fill_angle, fontname=fontname)
                            if random.random() >= 0.1:
                                self.dot.edge(f'{e_name}_error', f'{ov}_item', label='1  ', fontsize=pc_sz,
                                              arrowhead=arrow,
                                              arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname,
                                              color=edge_color)
                            else:
                                self.dot.edge(f'{e_name}_error', f'{ov}_item', arrowhead=arrow,
                                              arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname,
                                              color=edge_color)

                        elif (error_shape == 'self-loops') and (error != 'none'):
                            label = self._create_edge_label()
                            self.dot.edge(f'{ov}_item', f'{ov}_item', label=label, fontsize=pc_sz, arrowhead=arrow,
                                          arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)

                        curr_h_pos += 1

            for edges in self.lv_edges:
                # direction = random.random()
                if random.random() >= 0.1:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  label=self._create_edge_label(), fontsize=pc_sz,
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname, color=edge_color)
                else:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname, color=edge_color)

            if self.item_edges:
                for edges in self.ov_edges:
                    if random.random() >= 0.1:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item', label=self._create_edge_label(),
                                      fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname, color=edge_color)
                    else:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname, color=edge_color)

            # Generate some random text 
            str1 = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
            str2 = f"{random.choice(self.words)} {random.choice(self.words)} 9.021*** 0.8*"
            str3 = f"-0.34**, 0.87*** "
            str4 = f"-0.24**, {random.choice(self.words)} 0.17***"
            str5 = f"-0.912**, {random.choice(self.words)} 0.1319*** {random.choice(self.words)}"
            str6 = f"{random.choice(self.words)} -1.526**, {random.choice(self.words)} 0.187 {random.choice(self.words)}"
            str7 = f"{random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str8 = f"   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str9 = f"{random.choice(self.words)}   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str10 = f"{random.choice(self.words)}"
            str11 = f"{random.choice(self.words)}        {random.choice(self.words)}"
            random_list = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11]
            fontsize = str(random.choice([8, 12, 16, 20, 22]))

            if random.random() >= 0.9:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}', fontsize=fontsize, labelloc=label_pos[0],
                              labeljust=label_pos[1])
            elif random.random() >= 0.8:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}\n{random.choice(random_list)}',
                              fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.65:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.5:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)} {random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])

            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_circo.json', format='json'))
            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_circo.png', format='png'))
            # print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_circo', outfile=f'{self.output_path}_{edges_shape}_{l}_circo.json'))
            # print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_circo', outfile=f'{self.output_path}_{edges_shape}_{l}_circo.png'))
            # Delete unnecessary files
            os.remove(f'{self.output_path}_{edges_shape}_{l}_circo.json')
            os.remove(f'{self.output_path}_{edges_shape}_{l}_circo.png')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_circo.json.json',
                      f'{self.output_path}_{edges_shape}_{l}_circo.json')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_circo.png.png',
                      f'{self.output_path}_{edges_shape}_{l}_circo.png')
            # Generate annotation files
            generate_annotations(f'{self.output_path}_{edges_shape}_{l}_circo.json',
                                 f'{self.output_path}_{edges_shape}_{l}_circo.png')

    def generate_dot(self, n):

        for l in range(n):
            arrow = random.choice(scfg.ARROW_SHAPE)
            edges_shape = random.choice(scfg.EDGE_ATTR[:-2])
            width = random.choice(scfg.PENWIDTHS)
            arrow_sz = random.choice(scfg.ARROWSIZES)
            arrow_style = random.choice(scfg.STYLES)
            pc_sz = random.choice(scfg.PC_FONTSIZES)
            items = random.choice(scfg.ITEM_SHAPE)
            lv_shapes = random.choice(scfg.LV_SHAPE)
            fill_color = random.choice(scfg.COLORS) + ':' + random.choice(
                scfg.COLORS) if random.random() < 0 else '#FFFFFF'
            edge_color = random.choice(scfg.COLORS) if random.random() < 0.2 else '#000000'
            fill_angle = str(random.randint(0, 360))
            error = random.choice(scfg.ERRORS)
            error_shape = random.choice(scfg.ERROR_SHAPE)
            cluster = True if random.random() < 0.2 else False
            fontname = random.choice(scfg.FONTNAMES)
            rankdir = random.choice(scfg.RANK_DIR)
            label_pos = random.choice(scfg.LABEL_POS)

            self.dot = graphviz.Digraph(comment=f'SEM_{l}', format='png',
                                        graph_attr={'splines': edges_shape, 'rankdir': rankdir}, engine='dot')

            curr_h_pos = 0
            for ind, lv in enumerate(self.latent_variables):
                if cluster and (random.random() < 0.33):

                    with self.dot.subgraph(name=f'cluster_{lv}') as c:
                        cluster_color = random.choice(scfg.COLORS) if random.random() < 0.5 else '#FFFFFF'
                        if cluster_color != '#FFFFFF':
                            c.attr(style='filled', color=cluster_color)
                        else:
                            c.attr(color=random.choice(scfg.COLORS))
                        c.attr('node', shape=lv_shapes)

                        if len(lv) > 21:
                            fontsz = "8"
                        elif len(lv) > 15:
                            fontsz = "10"
                        elif len(lv) > 8:
                            fontsz = "12"
                        else:
                            fontsz = "14"

                        c.node(f'{lv}_construct', lv, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                               fontname=fontname, fontsize=fontsz)

                        c.attr('node', shape=items)
                        for ov in self.obs_vars[ind]:
                            c.node(f'{ov}_item', ov, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                   fontname=fontname)
                            if random.random() >= 0.2:
                                c.edge(f'{lv}_construct', f'{ov}_item', label=self._create_edge_label(), fontsize=pc_sz,
                                       arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                       penwidth=width, fontname=fontname, color=edge_color)
                            else:
                                c.edge(f'{lv}_construct', f'{ov}_item',
                                       arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                       penwidth=width, fontname=fontname, color=edge_color)
                            if (error_shape in ['circle', 'plaintext']) and (error != 'none'):
                                e_name = f'e{curr_h_pos}'
                                c.node(f'{e_name}_error', e_name, shape=error_shape, style='filled',
                                       fillcolor=fill_color, gradientangle=fill_angle, fontname=fontname)
                                if random.random() >= 0.1:
                                    c.edge(f'{e_name}_error', f'{ov}_item', label='1  ', fontsize=pc_sz,
                                           arrowhead=arrow,
                                           arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                                else:
                                    c.edge(f'{e_name}_error', f'{ov}_item', arrowhead=arrow,
                                           arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                                curr_h_pos += 1
                                e_name = f'e{curr_h_pos}'
                                if random.random() >= 0.1:
                                    self.dot.edge(f'{e_name}_error', f'{lv}_construct', label='1 ', fontsize=pc_sz,
                                                  arrowhead=arrow,
                                                  arrowsize=arrow_sz, style=arrow_style, penwidth=width,
                                                  fontname=fontname)
                                else:
                                    self.dot.edge(f'{e_name}_error', f'{lv}_construct', arrowhead=arrow,
                                                  arrowsize=arrow_sz, style=arrow_style, penwidth=width,
                                                  fontname=fontname)
                            elif (error_shape == 'self-loops') and (error != 'none'):
                                label = self._create_edge_label()
                                c.edge(f'{ov}_item', f'{ov}_item', label=label, fontsize=pc_sz, arrowhead=arrow,
                                       arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                            curr_h_pos += 1


                else:
                    self.dot.attr('node', shape=lv_shapes)

                    if len(lv) > 21:
                        fontsz = "8"
                    elif len(lv) > 15:
                        fontsz = "10"
                    elif len(lv) > 8:
                        fontsz = "12"
                    else:
                        fontsz = "14"

                    self.dot.node(f'{lv}_construct', lv, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                  fontname=fontname, fontsize=fontsz)

                    self.dot.attr('node', shape=items)
                    for ov in self.obs_vars[ind]:
                        self.dot.node(f'{ov}_item', ov, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                      fontname=fontname)
                        if random.random() >= 0.2:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item', label=self._create_edge_label(),
                                          fontsize=pc_sz,
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                        else:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item',
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                        if (error_shape in ['circle', 'plaintext']) and (error != 'none'):
                            e_name = f'e{curr_h_pos}'
                            self.dot.node(f'{e_name}_error', e_name, shape=error_shape, style='filled',
                                          fillcolor=fill_color, gradientangle=fill_angle, fontname=fontname)
                            if random.random() >= 0.1:
                                self.dot.edge(f'{e_name}_error', f'{ov}_item', label='1  ', fontsize=pc_sz,
                                              arrowhead=arrow,
                                              arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                            else:
                                self.dot.edge(f'{e_name}_error', f'{ov}_item', arrowhead=arrow,
                                              arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                            curr_h_pos += 1
                            e_name = f'e{curr_h_pos}'
                            if random.random() >= 0.1:
                                self.dot.edge(f'{e_name}_error', f'{lv}_construct', label='1 ', fontsize=pc_sz,
                                              arrowhead=arrow,
                                              arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                            else:
                                self.dot.edge(f'{e_name}_error', f'{lv}_construct', arrowhead=arrow,
                                              arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                        elif (error_shape == 'self-loops') and (error != 'none'):
                            label = self._create_edge_label()
                            self.dot.edge(f'{ov}_item', f'{ov}_item', label=label, fontsize=pc_sz, arrowhead=arrow,
                                          arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname,
                                          color=edge_color)
                        curr_h_pos += 1

            for edges in self.lv_edges:
                # direction = random.random()
                if random.random() >= 0.1:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  label=self._create_edge_label(), fontsize=pc_sz,
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname, color=edge_color)
                else:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname, color=edge_color)

            if self.item_edges:
                for edges in self.ov_edges:
                    if random.random() >= 0.1:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item', label=self._create_edge_label(),
                                      fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname, color=edge_color)
                    else:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname, color=edge_color)

            # Generate some random text 
            str1 = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
            str2 = f"{random.choice(self.words)} {random.choice(self.words)} 9.021*** 0.8*"
            str3 = f"-0.34**, 0.87*** "
            str4 = f"-0.24**, {random.choice(self.words)} 0.17***"
            str5 = f"-0.912**, {random.choice(self.words)} 0.1319*** {random.choice(self.words)}"
            str6 = f"{random.choice(self.words)} -1.526**, {random.choice(self.words)} 0.187 {random.choice(self.words)}"
            str7 = f"{random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str8 = f"   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str9 = f"{random.choice(self.words)}   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str10 = f"{random.choice(self.words)}"
            str11 = f"{random.choice(self.words)}        {random.choice(self.words)}"
            random_list = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11]
            fontsize = str(random.choice([8, 12, 16, 20, 22]))

            if random.random() >= 0.9:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}', fontsize=fontsize, labelloc=label_pos[0],
                              labeljust=label_pos[1])
            elif random.random() >= 0.8:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}\n{random.choice(random_list)}',
                              fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.65:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.5:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)} {random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])

            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_dot.json', format='json'))
            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_dot.png', format='png'))
            # Delete unnecessary files
            os.remove(f'{self.output_path}_{edges_shape}_{l}_dot.json')
            os.remove(f'{self.output_path}_{edges_shape}_{l}_dot.png')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_dot.json.json',
                      f'{self.output_path}_{edges_shape}_{l}_dot.json')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_dot.png.png',
                      f'{self.output_path}_{edges_shape}_{l}_dot.png')
            # Generate annotation files
            generate_annotations(f'{self.output_path}_{edges_shape}_{l}_dot.json',
                                 f'{self.output_path}_{edges_shape}_{l}_dot.png')

    def generate_dot_fc(self, n):

        for l in range(n):
            arrow = random.choice(scfg.ARROW_SHAPE)
            edges_shape = random.choice(scfg.EDGE_ATTR[:-2])
            width = random.choice(scfg.PENWIDTHS)
            arrow_sz = random.choice(scfg.ARROWSIZES)
            arrow_style = random.choice(scfg.STYLES)
            pc_sz = random.choice(scfg.PC_FONTSIZES)
            items = random.choice(scfg.ITEM_SHAPE)
            lv_shapes = random.choice(scfg.LV_SHAPE)
            fill_color = random.choice(scfg.COLORS) + ':' + random.choice(
                scfg.COLORS) if random.random() < 0 else '#FFFFFF'
            edge_color = random.choice(scfg.COLORS) if random.random() < 0.15 else '#000000'
            fill_angle = str(random.randint(0, 360))
            error = random.choice(scfg.ERRORS)
            error_shape = random.choice(scfg.ERROR_SHAPE)
            cluster = True if random.random() < 0.5 else False
            fontname = random.choice(scfg.FONTNAMES)
            rankdir = random.choice(scfg.RANK_DIR)
            label_pos = random.choice(scfg.LABEL_POS)

            observed_vars = []

            self.dot = graphviz.Digraph(comment=f'SEM_{l}', format='png', graph_attr={'rankdir': rankdir}, engine='dot')

            curr_h_pos = 0
            for ind, lv in enumerate(self.latent_variables):

                self.dot.attr('node', shape=lv_shapes)

                if len(lv) > 21:
                    fontsz = "8"
                elif len(lv) > 15:
                    fontsz = "10"
                elif len(lv) > 8:
                    fontsz = "12"
                else:
                    fontsz = "14"

                self.dot.node(f'{lv}_construct', lv, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                              fontname=fontname, fontsize=fontsz)

                self.dot.attr('node', shape=items)
                for ov in self.obs_vars[ind]:
                    self.dot.node(f'{ov}_item', ov, style='filled', fillcolor=fill_color, gradientangle=fill_angle,
                                  fontname=fontname)
                    observed_vars.append(ov)

            for lv in self.latent_variables:
                for ov in observed_vars:

                    if random.random() >= 0.1:
                        if random.random() >= 0.2:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item', dir='forward',
                                          label=self._create_edge_label(), fontsize=pc_sz,
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                        else:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item', dir='both', label=self._create_edge_label(),
                                          fontsize=pc_sz,
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                    else:
                        if random.random() >= 0.2:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item', dir='forward',
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)
                        else:
                            self.dot.edge(f'{lv}_construct', f'{ov}_item', dir='both',
                                          arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                          penwidth=width, fontname=fontname, color=edge_color)

            # Generate some random text 
            str1 = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
            str2 = f"{random.choice(self.words)} {random.choice(self.words)} 9.021*** 0.8*"
            str3 = f"-0.34**, 0.87*** "
            str4 = f"-0.24**, {random.choice(self.words)} 0.17***"
            str5 = f"-0.912**, {random.choice(self.words)} 0.1319*** {random.choice(self.words)}"
            str6 = f"{random.choice(self.words)} -1.526**, {random.choice(self.words)} 0.187 {random.choice(self.words)}"
            str7 = f"{random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str8 = f"   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str9 = f"{random.choice(self.words)}   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str10 = f"{random.choice(self.words)}"
            str11 = f"{random.choice(self.words)}        {random.choice(self.words)}"
            random_list = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11]
            fontsize = str(random.choice([8, 12, 16, 20, 22]))

            if random.random() >= 0.9:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}', fontsize=fontsize, labelloc=label_pos[0],
                              labeljust=label_pos[1])
            elif random.random() >= 0.8:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}\n{random.choice(random_list)}',
                              fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.65:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.5:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)} {random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])

            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_dot_fc.json', format='json'))
            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_dot_fc.png', format='png'))
            # Delete unnecessary files
            os.remove(f'{self.output_path}_{edges_shape}_{l}_dot_fc.json')
            os.remove(f'{self.output_path}_{edges_shape}_{l}_dot_fc.png')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_dot_fc.json.json',
                      f'{self.output_path}_{edges_shape}_{l}_dot_fc.json')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_dot_fc.png.png',
                      f'{self.output_path}_{edges_shape}_{l}_dot_fc.png')
            # Generate annotation files
            generate_annotations(f'{self.output_path}_{edges_shape}_{l}_dot_fc.json',
                                 f'{self.output_path}_{edges_shape}_{l}_dot_fc.png')

    def generate_neato(self, n):

        for l in range(n):
            arrow = random.choice(scfg.ARROW_SHAPE)
            edges_shape = random.choice(scfg.EDGE_ATTR)
            width = random.choice(scfg.PENWIDTHS)
            arrow_sz = random.choice(scfg.ARROWSIZES)
            arrow_style = random.choice(scfg.STYLES)
            pc_sz = random.choice(scfg.PC_FONTSIZES)
            items = random.choice(scfg.ITEM_SHAPE)
            lv_shapes = random.choice(scfg.LV_SHAPE)
            fill_color = random.choice(scfg.COLORS) + ':' + random.choice(
                scfg.COLORS) if random.random() < 0.5 else '#FFFFFF'
            fill_angle = str(random.randint(0, 360))
            error = random.choice(scfg.ERRORS)
            error_shape = random.choice(scfg.ERROR_SHAPE)
            fontname = random.choice(scfg.FONTNAMES)
            label_pos = random.choice(scfg.LABEL_POS)

            self.dot = graphviz.Digraph(comment=f'SEM_{l}', format='png', graph_attr={'splines': edges_shape},
                                        engine='neato')

            # Check amount of nodes and set positioning
            n = len(self.latent_variables)
            if len(self.latent_variables) % 2 == 0:
                positions = [
                    [f'{(1 - n // 2) + 2 * i},{-1}!' if i < n // 2 else f'{(1 - n // 2) + 2 * (i - n // 2)},{1}!' for i
                     in range(n)],
                    [f'{-1},{(1 - n // 2) + 2 * i}!' if i < n // 2 else f'{1},{(1 - n // 2) + 2 * (i - n // 2)}!' for i
                     in range(n)]]
            else:
                positions = [
                    [f'{(1 - n // 2) + 2 * i},{-1}!' if i < n // 2 else f'{-(n // 2) + 2 * (i - n // 2)},{1}!' for i in
                     range(n)],
                    [f'{-1},{(1 - n // 2) + 2 * i}!' if i < n // 2 else f'{1},{-(n // 2) + 2 * (i - n // 2)}!' for i in
                     range(n)],
                    [f'{(1 - n // 2) + 2 * i},{1}!' if i < n // 2 else f'{-(n // 2) + 2 * (i - n // 2)},{-1}!' for i in
                     range(n)],
                    [f'{1},{(1 - n // 2) + 2 * i}!' if i < n // 2 else f'{-1},{-(n // 2) + 2 * (i - n // 2)}!' for i in
                     range(n)]]

            # Create nodes for latent variables
            self.dot.attr('node', shape=lv_shapes)
            curr_positions = 1
            pos = positions[curr_positions]
            for ind, lv in enumerate(self.latent_variables):

                if len(lv) > 21:
                    fontsz = "8"
                elif len(lv) > 15:
                    fontsz = "10"
                elif len(lv) > 8:
                    fontsz = "12"
                else:
                    fontsz = "14"

                self.dot.node(f'{lv}_construct', lv, pos=pos[ind], style='filled', fillcolor=fill_color,
                              gradientangle=fill_angle, fontname=fontname, fontsize=fontsz)
                if error == 'both':
                    label = self._create_edge_label()
                    self.dot.edge(f'{lv}_construct', f'{lv}_construct', label=label, fontsize=pc_sz, arrowhead=arrow,
                                  arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
            self.dot.attr('node', shape=items)

            # position the items
            if curr_positions % 2 == 0:
                vert_pos = [int(position.split(',')[-1][:-1]) for position in pos]
                # 1. figure out how many items per level
                amount_n = sum([self.amount_obs_vars[ind] for ind, pos in enumerate(vert_pos) if pos == +1])
                amount_s = sum([self.amount_obs_vars[ind] for ind, pos in enumerate(vert_pos) if pos == -1])
                # 2. distribute items
                v_dist = random.randint(2, 3)
                e = self._place_neato_objects(self.dot, self.obs_vars, self.latent_variables, pos, vert_pos,
                                              f'{-amount_n // 2 + 1},{1 + v_dist}!',
                                              'filled', fill_color, fill_angle, pc_sz, arrow, arrow_sz, arrow_style,
                                              width, amount_n, 'hor',
                                              error, error_shape, fontname=fontname)
                self._place_neato_objects(self.dot, self.obs_vars, self.latent_variables, pos, vert_pos,
                                          f'{-amount_s // 2 + 1},{-1 - v_dist}!',
                                          'filled', fill_color, fill_angle, pc_sz, arrow, arrow_sz, arrow_style, width,
                                          amount_s, 'hor',
                                          error, error_shape, e, fontname=fontname)

            else:
                vert_pos = [int(position.split(',')[0]) for position in pos]
                # 1. figure out how many items per level
                amount_e = sum([self.amount_obs_vars[ind] for ind, pos in enumerate(vert_pos) if pos == +1])
                amount_w = sum([self.amount_obs_vars[ind] for ind, pos in enumerate(vert_pos) if pos == -1])
                # 2. distribute items
                v_dist = random.randint(2, 3)
                e = self._place_neato_objects(self.dot, self.obs_vars, self.latent_variables, pos, vert_pos,
                                              f'{1 + v_dist},{-amount_e // 2 + 1}!',
                                              'filled', fill_color, fill_angle, pc_sz, arrow, arrow_sz, arrow_style,
                                              width, amount_e, 'ver',
                                              error, error_shape, fontname=fontname)
                self._place_neato_objects(self.dot, self.obs_vars, self.latent_variables, pos, vert_pos,
                                          f'{-1 - v_dist},{-amount_w // 2 + 1}!',
                                          'filled', fill_color, fill_angle, pc_sz, arrow, arrow_sz, arrow_style, width,
                                          amount_w, 'ver',
                                          error, error_shape, e, fontname=fontname)

            for edges in self.lv_edges:
                # direction = random.random()
                if random.random() >= 0.1:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  label=self._create_edge_label(), fontsize=pc_sz,
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname)
                else:
                    self.dot.edge(f'{edges[0]}_construct', f'{edges[1]}_construct', dir=edges[2],
                                  arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                  penwidth=width, fontname=fontname)

            if self.item_edges:
                for edges in self.ov_edges:
                    if random.random() >= 0.1:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item', label=self._create_edge_label(),
                                      fontsize=pc_sz,
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)
                    else:
                        self.dot.edge(f'{edges[0]}_item', f'{edges[1]}_item',
                                      arrowhead=arrow, arrowtail=arrow, arrowsize=arrow_sz, style=arrow_style,
                                      penwidth=width, fontname=fontname)

            # Generate some random text 
            str1 = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
            str2 = f"{random.choice(self.words)} {random.choice(self.words)} 9.021*** 0.8*"
            str3 = f"-0.34**, 0.87*** "
            str4 = f"-0.24**, {random.choice(self.words)} 0.17***"
            str5 = f"-0.912**, {random.choice(self.words)} 0.1319*** {random.choice(self.words)}"
            str6 = f"{random.choice(self.words)} -1.526**, {random.choice(self.words)} 0.187 {random.choice(self.words)}"
            str7 = f"{random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str8 = f"   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str9 = f"{random.choice(self.words)}   {random.choice(self.words)} {random.choice(self.words)}    {random.choice(self.words)}"
            str10 = f"{random.choice(self.words)}"
            str11 = f"{random.choice(self.words)}        {random.choice(self.words)}"
            random_list = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11]
            fontsize = str(random.choice([8, 12, 16, 20, 22]))

            if random.random() >= 0.9:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}', fontsize=fontsize, labelloc=label_pos[0],
                              labeljust=label_pos[1])
            elif random.random() >= 0.8:
                self.dot.attr(label=f'\n\n{random.choice(random_list)}\n{random.choice(random_list)}',
                              fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.65:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])
            elif random.random() >= 0.5:
                self.dot.attr(
                    label=f'\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)}\n{random.choice(random_list)} {random.choice(random_list)}',
                    fontsize=fontsize, labelloc=label_pos[0], labeljust=label_pos[1])

            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_neato.json', format='json'))
            print(self.dot.render(f'{self.output_path}_{edges_shape}_{l}_neato.png', format='png'))
            # Delete unnecessary files
            os.remove(f'{self.output_path}_{edges_shape}_{l}_neato.json')
            os.remove(f'{self.output_path}_{edges_shape}_{l}_neato.png')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_neato.json.json',
                      f'{self.output_path}_{edges_shape}_{l}_neato.json')
            os.rename(f'{self.output_path}_{edges_shape}_{l}_neato.png.png',
                      f'{self.output_path}_{edges_shape}_{l}_neato.png')
            # Generate annotation files
            generate_annotations(f'{self.output_path}_{edges_shape}_{l}_neato.json',
                                 f'{self.output_path}_{edges_shape}_{l}_neato.png')

    def _place_neato_objects(self, dot_obj, obs_vars, latent_variables, pos, vert_pos, position,
                             style, color, angle, pc_sz, arrow, arrow_sz, arrow_style, width,
                             amount, orientation, errors, error_shape, curr_e_name=0, fontname=""):

        curr_h_pos = 0

        if orientation == 'hor':
            if int(position.split(',')[-1][:-1]) > 0:
                filter_pos = +1
            else:
                filter_pos = -1
        elif orientation == 'ver':
            if int(position.split(',')[0]) > 0:
                filter_pos = +1
            else:
                filter_pos = -1

        for node in [ind for ind, pos in enumerate(vert_pos) if pos == filter_pos]:
            node_x_pos = int(pos[node].split(',')[0])
            for var in obs_vars[node]:
                if orientation == 'hor':
                    y_pos = int(position.split(',')[-1][:-1])
                    position = f'{-amount // 2 + 2 * curr_h_pos},{y_pos}!'
                    if errors != 'none':
                        pos_err = f'{-amount // 2 + 2 * curr_h_pos},{y_pos + filter_pos}!'
                elif orientation == 'ver':
                    x_pos = int(position.split(',')[0])
                    position = f'{x_pos},{-amount // 2 + 2 * curr_h_pos}!'
                    if errors != 'none':
                        pos_err = f'{x_pos + filter_pos},{-amount // 2 + 2 * curr_h_pos}!'

                dot_obj.node(f'{var}_item', var, pos=position, style=style, fillcolor=color, gradientangle=angle,
                             fontname=fontname)
                label = self._create_edge_label()
                if random.random() >= 0.2:
                    dot_obj.edge(f'{latent_variables[node]}_construct', f'{var}_item', label=label, fontsize=pc_sz,
                                 arrowhead=arrow, arrowsize=arrow_sz, style=arrow_style, penwidth=width,
                                 fontname=fontname)
                else:
                    dot_obj.edge(f'{latent_variables[node]}_construct', f'{var}_item',
                                 arrowhead=arrow, arrowsize=arrow_sz, style=arrow_style, penwidth=width,
                                 fontname=fontname)
                if (error_shape in ['circle', 'plaintext']) and (errors != 'none'):
                    e_name = f'e{curr_e_name + curr_h_pos}'
                    dot_obj.node(f'{e_name}_error', e_name, shape=error_shape, pos=pos_err, style=style,
                                 fillcolor=color, gradientangle=angle, fontname=fontname)
                    if random.random() >= 0.1:
                        dot_obj.edge(f'{e_name}_error', f'{var}_item', label='1  ', fontsize=pc_sz, arrowhead=arrow,
                                     arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                    else:
                        dot_obj.edge(f'{e_name}_error', f'{var}_item', arrowhead=arrow,
                                     arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                elif (error_shape == 'self-loops') and (errors != 'none'):
                    label = self._create_edge_label()
                    dot_obj.edge(f'{var}_item', f'{var}_item', label=label, fontsize=pc_sz, arrowhead=arrow,
                                 arrowsize=arrow_sz, style=arrow_style, penwidth=width, fontname=fontname)
                curr_h_pos += 1

        return curr_h_pos

    def _create_edge_label(self):
        significance = random.choice(['', '', '', '*', '**', '***'])
        sign = random.choice(['', '', '-'])
        if random.random() >= 0.5:
            second_line = random.choice(['t', 'x', 'y', 'a', 's', 'H', 'h', 'f']) + " = " + str(
                round(random.random(), 3))
            label = f'''<
                        <table border="0" cellborder="0">
                            <tr>
                                <td bgcolor="white"> {sign}{round(random.random(), 2)}{significance}</td>
                            </tr>
                            <tr>
                                <td bgcolor="white">{second_line}</td>
                            </tr>
                        </table>
                        >'''
        else:
            if random.random() < 0.3:
                number = 1
            else:
                digits = random.choice([2, 3, 4])
                number = round(random.random(), digits)

            label = f'''<
                        <table border="0" cellborder="0">
                            <tr>
                                <td bgcolor="white">{sign}{number}</td>
                            </tr>
                        </table>>'''
        return label

    def _edge_directions(self):
        if self.n2 > 2:
            edge_lst = random.sample(list(itertools.combinations(self.latent_variables, 2)),
                                     random.randint(self.n1 // 2, self.n2 - 1))
        else:
            edge_lst = [[self.latent_variables[0], self.latent_variables[1]]]
        unique_nodes = [item for pair in edge_lst for item in pair]
        for lv in self.latent_variables:
            if not lv in set(unique_nodes):
                if lv != self.latent_variables[0]:
                    edge_lst.append((lv, self.latent_variables[0]))
                else:
                    edge_lst.append((lv, self.latent_variables[-1]))
        return [[edge[0], edge[1], 'both'] if random.random() < 0.3 else [edge[0], edge[1], 'forward'] for edge in
                edge_lst]
