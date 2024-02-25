# from webconflib import * # pylint: disable=W0401,W0614
from manim import Graph, Scene, VGroup, Line, Circle, Restore, MovingCameraScene, Table, \
    Create, FadeIn, FadeOut, Transform, DecimalTable, \
    UP, DOWN, DEFAULT_STROKE_WIDTH, Text, \
    SurroundingRectangle, \
    GREEN, GRAY, RED, BLUE, YELLOW, PURPLE, WHITE, PINK, GOLD, TEAL, ORANGE, DARK_BROWN

import networkx as nx
import numpy as np

CENTER_L = np.array([-3, 0, 0])
CENTER_R = np.array([2, 0, 0])

CMAP = [
    (GREEN, GOLD),
    (YELLOW, PURPLE)
]

class MyExampleGraph:
    def __init__(self, N=50, F=None, homophily=None, heterophily=None, seed=1234):
        np.random.seed(seed)
        nodes = np.arange(N)
        sigmoid = lambda x: 1 / (1 + np.exp(-x))
        F = np.random.randint(low=-1, high=2, size=(N, 4)) if F is None else F
        homophily = {0: 3, 1: 0, 2: 0.3, 3: -0.8} if homophily is None else homophily
        heterophily = {0: -3, 1: 3, 2: -0.3, 3: 0.8} if heterophily is None else heterophily
        
        assert F.shape[0] == N
        
        edges = []
        for u in range(N):
            for v in range(N):
                if u != v:
                    p = sum(
                        0 if (F[u, h] * F[v, h] == 0)
                        else (homophily[h] if F[u, h] == F[v, h] else heterophily[h])
                        for h in range(F.shape[1])
                    )
                    if np.random.random() < sigmoid(p - 3):
                        edges += [(u, v)]

        self.nx_G = nx.Graph()
        self.nx_G.add_nodes_from(nodes)
        self.nx_G.add_edges_from(edges)
        self.F = F
        self.nodes = nodes
        self.layout = None
        self.N = N
        print(self.nx_G.number_of_nodes(), "nodes,", self.nx_G.number_of_edges(), "edges")
    
    def get_single_layout(self, subgraph=None):
        if subgraph is None:
            subgraph = self.nx_G
        layout = nx.layout.circular_layout(subgraph, scale=3, dim=3, center=np.array([-0.5, 0, 0]))
        layout = {i: 
            # p * np.array([1.5, 1, 1]) + np.array([0.25, 0, 0])
            p * np.array([1.75, 1, 1]) + np.array([0.375, 0, 0])
            for i, p in layout.items()
        }
        return layout
    
    def get_split_layout(self, feature):
        layout_O = self.get_single_layout()
        
        nodes_L = self.nodes[self.F[:, feature] == -1]
        nodes_R = self.nodes[self.F[:, feature] == 1]
        # nodes_O = self.nodes[self.F[:, feature] == 0]
        # layout_O = self.get_single_layout(subgraph=nx.subgraph(self.nx_G, nodes_O))
        layout_P = nx.layout.circular_layout(nx.subgraph(self.nx_G, nodes_L),
            scale=1.2, dim=3, center=CENTER_L)
        layout_N = nx.layout.circular_layout(nx.subgraph(self.nx_G, nodes_R),
            scale=1.2, dim=3, center=CENTER_R)
        return {**layout_O, **layout_P, **layout_N}
    
    def vertex_colors(self, h, cmap=None):
        cmap = CMAP[h] if cmap is None else cmap
        return {i: {
            "fill_color": WHITE if self.F[i, h] == 0 else cmap[(self.F[i, h] + 1) // 2],
            "radius": 0.15
        } for i in self.nodes}
    
    def edge_type(self, u, v, h):
        return 0 if self.F[u, h] * self.F[v, h] ==0 else (1 if self.F[u, h] == self.F[v, h] else -1)
    
    def iterate_edge_with_types(self, feature):
        for u, v in self.nx_G.edges:
            yield u, v, self.edge_type(u, v, feature)
            
    def edge_config(self, h):
        return {(u, v): {
            'stroke_opacity': 0.5 if t == 0 else 1,
            'stroke_width': (0.25 if t == 0 else 1) * DEFAULT_STROKE_WIDTH,
            'stroke_color': RED if t == -1 else BLUE if t == 1 else '#999999',
        } for u, v, t in self.iterate_edge_with_types(h)}
    
    def get_example_edge(self, feature, edge_type=-1):
        u, v = next((u, v)
            for u, v, t in self.iterate_edge_with_types(feature=feature) if t == edge_type
        )
        u, v = (u, v) if self.F[feature, u] == -1 else (v, u)
        
        circle_u = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        circle_v = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        circle_u.shift(self.layout[u])
        circle_v.shift(self.layout[v])
        print(u, v, self.layout[u], self.layout[v])
        edge = Line(self.layout[u], self.layout[v])
        return VGroup(circle_u, circle_v, edge)
        
    
    def to_manim(self, feature=None, highlight_edges=False, color_feature=None,
            vertex_cmap=None, subgraph=None, layout=None):
        edge_config = {
            'stroke_opacity': 0.5,
            'stroke_width': 0.25 * DEFAULT_STROKE_WIDTH,
            'stroke_color': '#999999'
        }
        
        if feature is not None:
            self.layout = self.get_split_layout(feature) if layout is None else layout
            if highlight_edges:
                edge_config |= self.edge_config(feature)
        else:
            self.layout = self.get_single_layout() if layout is None else layout
        
        vertex_config = {"fill_color": WHITE, "radius": 0.125}
        if color_feature is not None:
            vertex_config = {**vertex_config, **self.vertex_colors(color_feature, cmap=vertex_cmap)}
        
        nx_graph = self.nx_G if subgraph is None else subgraph
        return Graph.from_networkx(nx_graph,
            layout=self.layout,
            layout_scale=5,
            edge_config=edge_config,
            vertex_config=vertex_config,
        )
        
class GraphScene(Scene):
    def construct_graph_scene(self, original_graph=None):
        G = MyExampleGraph()
        vis_g = G.to_manim()
        
        if original_graph is not None:
            pos = list(G.layout.values())
            np.random.shuffle(pos)
            self.play(*[node.animate.move_to(pos[i]) for i, node in enumerate(original_graph)],
                run_time=1.5)
            self.play(Create(vis_g), FadeOut(original_graph), run_time=3)
        else:
            self.add(vis_g)
        
        circle_feat_0_L = Circle(radius=1.5, color=CMAP[0][0], stroke_width=8).shift(CENTER_L)
        circle_feat_0_R = Circle(radius=1.5, color=CMAP[0][1], stroke_width=8).shift(CENTER_R)
        
        circle_feat_1_L = Circle(radius=1.5, color=CMAP[1][0], stroke_width=8).shift(CENTER_L)
        circle_feat_1_R = Circle(radius=1.5, color=CMAP[1][1], stroke_width=8).shift(CENTER_R)
        
        # self.wait(1.5)
        self.play(Transform(vis_g, G.to_manim(color_feature=0)))
        self.wait(0.5)
        self.play(Transform(vis_g, G.to_manim(feature=0)),
            Create(circle_feat_0_L), Create(circle_feat_0_R), run_time=2)
        self.play(Transform(vis_g, G.to_manim(feature=0, highlight_edges=True)))
        self.wait(0.25)
        
        reset_vis_g = G.to_manim()
        self.play(Transform(vis_g, reset_vis_g), FadeOut(circle_feat_0_L), FadeOut(circle_feat_0_R))
        self.wait(0.25)
        
        self.play(Transform(vis_g, G.to_manim(color_feature=1)))
        self.wait(0.5)
        self.play(Transform(vis_g, G.to_manim(feature=1)),
            Create(circle_feat_1_L), Create(circle_feat_1_R), run_time=2)
        self.play(Transform(vis_g, G.to_manim(feature=1, highlight_edges=True)))
        self.wait(0.5)
        
        vis_edge = G.get_example_edge(feature=1)
        self.play(FadeOut(vis_g), FadeIn(vis_edge))
        self.wait(0.2)
        return vis_edge, (circle_feat_1_L, circle_feat_1_R)
        
        # self.play(Transform(vis_g, G.to_manim()),
        #     FadeOut(circle_feat_1_L), FadeOut(circle_feat_1_R))
        # self.play(FadeOut(vis_g))
        # 
        # self.play(FadeIn(G.get_example_edge(feature=1)))
        # self.wait(2)
        
        # self.play(FadeOut(vis_g))
    
    def construct(self):
        self.construct_graph_scene()
        self.play(*[FadeOut(mob)for mob in self.mobjects])

class FocusGraphScene(MovingCameraScene):
    def construct(self):
        G = MyExampleGraph()
        vis_g = G.to_manim()
        self.add(vis_g)
        self.camera.frame.save_state()
        
        table_g = DecimalTable([
            [27976, 34060, 31997, 21225, 29045],
            [1166076, 1390243, 1221779, 793569, 1067614]
        ],
            col_labels=[Text(y) for y in "2016 2017 2018 2019 2020".split()],
            row_labels=[Text("Num. nodes"), Text("Num. edges")],
            element_to_mobject_config={"num_decimal_places": 0},
        ).scale(0.4).shift(4.5 * UP)
        self.play(
            self.camera.frame.animate.move_to(table_g).set(width=table_g.width*1.2),
            FadeIn(table_g)
        )
        self.wait(5)
        # self.play(Restore(self.camera.frame), FadeOut(table_g),)
        
        node = vis_g[10]
        
        color_copies = VGroup(*[
            node.copy().set_fill(c, opacity=0.75) for c in
            [TEAL, GREEN, PURPLE, PINK, ORANGE, RED, DARK_BROWN, GRAY]
        ])
        self.play(
            self.camera.frame.animate.move_to(node).set(width=node.width*4),
            FadeOut(table_g),
            FadeIn(color_copies),
            *(
                [n.animate.set_fill(opacity=0.05) for n in vis_g if n != node] +
                [e.animate.set_stroke(opacity=0.05) for e in vis_g.edges.values()]
            )
        )

        table = Table([
            ["Young", "Male", "Poor", "Left"],
            ["Old", "Female", "Rich", "Right"]],
            line_config={"stroke_width": 2, "color": WHITE}
        ).scale(0.15).next_to(node, 0.5 * UP)
        
        self.play(
            table.create(),
            color_copies.animate.arrange_in_grid(rows=2).shift(DOWN*0.4),
            self.camera.frame.animate.move_to(node).set(width=node.width*12),
        )
        self.wait(3)
        hl1 = SurroundingRectangle(table.get_columns()[:-1])
        hl2 = SurroundingRectangle(table.get_columns()[-1])
        self.play(Create(hl1))
        self.wait(2.5)
        self.play(
            FadeOut(hl1),
            Create(hl2)
        )
        self.wait(2.5)
        
        self.play(
            Restore(self.camera.frame), 
            FadeOut(color_copies),
            FadeOut(table),
            FadeOut(hl2),
            *(
                # [c.animate.move_to(node.get_center()) for c in color_copies] +
                [n.animate.set_fill(opacity=1) for n in vis_g if n != node] +
                [e.animate.set_stroke(opacity=0.5) for e in vis_g.edges.values()]
            )
        )
