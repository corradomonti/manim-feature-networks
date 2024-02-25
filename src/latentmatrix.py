from manim import Scene, VGroup, DashedLine, Circle, Arc, Matrix, Tex, \
    DashedVMobject, Write, \
    FadeIn, FadeOut, Transform, GrowFromCenter, GrowFromPoint, \
    RIGHT, LEFT, DOWN, UP, PI, DEFAULT_STROKE_WIDTH, \
    GREEN, YELLOW, PURPLE, WHITE, BLACK, GOLD

import numpy as np

CMAP = [
    (GREEN, GOLD),
    (YELLOW, PURPLE)
]
N_FEAT = sum(map(len, CMAP))

class Feature(Circle):
    def __init__(self, args):
        feature, value, on = args
        # position = DOWN * (feature * 2 + (1 if value == 1 else 0)) #arc_center=position
        
        if on:
            color = CMAP[feature][(value + 1) // 2]
            super().__init__(radius=0.2,
                stroke_color=color, stroke_width = 2 * DEFAULT_STROKE_WIDTH,
                # fill_color=color, fill_opacity=1, stroke_opacity=0
            )
        else:
            super().__init__(radius=0.2, stroke_color='#999999')
            dashes = DashedVMobject(self, num_dashes=12, dashed_ratio=1/4)
            self.clear_points()
            self.add(*dashes)
            
class FeaturePair(VGroup):
    def __init__(self, args):
        feature1, value1, feature2, value2, radius = args
        if np.sum(radius) == 0:
            # cicle = DashedVMobject(
                # Circle(radius=0.2, stroke_color='#999999'), num_dashes=12, dashed_ratio=1/4)
            circle = Circle(radius=0.2, stroke_color=BLACK)
            super().__init__(circle)
        else:
            color1 = CMAP[feature1][(value1 + 1) // 2]
            color2 = CMAP[feature2][(value2 + 1) // 2]
            
            half1 = Arc(angle=PI, start_angle=PI/2,
                radius=radius, fill_color=color1, fill_opacity=1, stroke_opacity=0)
            half2 = Arc(angle=PI, start_angle=3/2 * PI,
                radius=radius, fill_color=color2, fill_opacity=1, stroke_opacity=0)
            super().__init__(half1, half2)

class FeatureVector:
    def __init__(self, F_u, position=lambda x: x):
        assert len(F_u) == len(CMAP)
        self.F_u = F_u
        self.position = position
    
    def to_symbol_vis(self):
        x_u_args = [ [(h, v, self.F_u[h] == v)] for h in range(len(self.F_u)) for v in (-1, 1)]
        vis = Matrix(x_u_args, element_to_mobject=Feature)
        self.position(vis)
        return vis
    
    def to_formal_vis(self):
        vis = Matrix([[r"x_{u, %d}" % i] for i in range(N_FEAT)])
        self.position(vis)
        return vis
        

class WMatrix:
    def to_symbol_vis(self, radius=0.2):
        features = [ [f, v] for f in range(len(CMAP)) for v in (-1, 1)]
        w_args = [[tuple(h + k + [radius]) for k in features] for h in features]
        return Matrix(w_args, element_to_mobject=FeaturePair)
    
    def to_formal_vis(self):
        return Matrix([[r"W_{%d, %d}" % (h, k) for k in range(N_FEAT)] for h in range(N_FEAT)])
    
    def to_example_vis(self, matrix):
        features = [ [f, v] for f in range(len(CMAP)) for v in (-1, 1)]
        w_args = [[tuple(h + k + [matrix[i, j]])
            for i, k in enumerate(features)] for j, h in enumerate(features)]
        return Matrix(w_args, element_to_mobject=FeaturePair)
        
class MatrixScene(Scene):
    def construct_matrix_scene(self, transform_edge_from=None, feature_circles=None):
        node_u = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        node_v = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        # node_u.shift(np.array([-4, 0, 0]))
        # node_v.shift(np.array([-0.5, 2, 0]))
        
        
        CENTER_L = np.array([-2.5, 0, 0])
        CENTER_R = np.array([2.5, 0, 0])
        
        node_u.shift(CENTER_L)
        node_v.shift(CENTER_R)
        line = DashedLine(CENTER_L, CENTER_R)
        
        edge_and_nodes = VGroup(node_u, node_v, line)
        
        if transform_edge_from is None:
            self.play(GrowFromPoint(edge_and_nodes, CENTER_L))
        else:
            self.play(Transform(transform_edge_from, edge_and_nodes))
            edge_and_nodes = transform_edge_from
        
        u_tex = Tex("$x_u$")
        v_tex = Tex("$x_v$")
        u_tex.next_to(node_u, LEFT)
        v_tex.next_to(node_v, RIGHT)
        
        x_u = FeatureVector([-1, -1], position=lambda x: x.next_to(u_tex, LEFT))
        x_v = FeatureVector([-1, 1], position=lambda x: x.next_to(v_tex, RIGHT))
        x_u_vis = x_u.to_formal_vis()
        x_v_vis = x_v.to_formal_vis()
        x_u_circle = Feature((1, -1, True))
        x_u_circle.next_to(x_u_vis.elements[2], RIGHT)
        x_v_circle = Feature((1, 1, True))
        x_v_circle.next_to(x_v_vis.elements[3], LEFT)
        feature_circle_anims = [] if feature_circles is None else [
                Transform(feature_circles[0], x_u_circle),
                Transform(feature_circles[1], x_v_circle)
        ]
        self.play(*(
            [GrowFromCenter(t) for t in (u_tex, v_tex, x_u_vis, x_v_vis)] +
            feature_circle_anims
        ))
        
        self.wait(2)
        x_u_vis_symb = x_u.to_symbol_vis()
        x_v_vis_symb = x_v.to_symbol_vis()
        
        feature_circle_fade_outs = [] if feature_circles is None else [
                Transform(feature_circles[0], x_u_vis_symb.elements[2]),
                Transform(feature_circles[1], x_v_vis_symb.elements[3])
        ]
        self.play(
            Transform(x_u_vis, x_u_vis_symb),
            Transform(x_v_vis, x_v_vis_symb),
            *feature_circle_fade_outs)
        if feature_circles is not None:
            for c in feature_circles:
                self.remove(c)
        self.wait(1.5)
        
        y_tex = Tex(r"$y_{u, v}$")
        y_tex.next_to(line, UP)
        self.play(GrowFromCenter(y_tex))
        self.wait(0.25)

        formula = Tex(r"$\textrm{logit}(y_{u, v}) = \beta_0 + x_u^\top W x_v$")
        formula.shift(np.array([0, 3, 0]))
        self.play(GrowFromCenter(formula))
        
        self.wait(2)
        
        w = WMatrix()
        w_vis = w.to_formal_vis()
        w_tex = Tex(r"$W$")
        w_tex.next_to(w_vis, DOWN)
        
        self.play(
            u_tex.animate.next_to(x_u_vis, DOWN),
            x_v_vis.animate.shift(np.array([-4, 3, 0])).rotate(PI / 2),
            v_tex.animate.shift(np.array([-5.2, 3, 0])),
            formula.animate.shift(np.array([0, -6.5, 0])),
            FadeOut(edge_and_nodes),
            FadeOut(y_tex),
            GrowFromCenter(w_vis),
            FadeIn(w_tex),
        )
        
        self.wait(3)
        
        self.play(
            Transform(w_vis, w.to_symbol_vis())
        )
        
        self.wait(3)
        
        self.play(
            Transform(w_vis, w.to_example_vis(0.2 * np.array([
                [0.75, 0, 0, 0],
                [0, 2, 0, 0],
                [0, 0, 0.5, 0],
                [0, 0, 0, 1.],
            ])))
        )
        
        self.wait(2)
        
        self.play(
            Transform(w_vis, w.to_example_vis(0.2 * np.array([
                [0, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 1.5],
                [0, 0, 1.5, 0],
            ])))
        )
        
        self.wait(2)
        
        # self.play(
        #     Transform(w_vis, w.to_example_vis(0.2 * np.array([
        #         [1.25, 0, 0, 0],
        #         [0, 1.25, 0, 0],
        #         [0, 0, 0, 1.25],
        #         [0, 0, 1.2, 0],
        #     ])))
        # )
        # 
        # self.wait(2)
    
    def construct(self):
        self.construct_matrix_scene()
        self.play(*[FadeOut(mob)for mob in self.mobjects])




class MatrixTopicScene(Scene):
    def construct(self):
        node_u = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        node_v = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        CENTER_L = np.array([-2.5, 0, 0])
        CENTER_R = np.array([2.5, 0, 0])
        node_u.shift(CENTER_L)
        node_v.shift(CENTER_R)
        u_tex = Tex("$x_u$")
        v_tex = Tex("$x_v$")
        u_tex.next_to(node_u, LEFT)
        v_tex.next_to(node_v, RIGHT)
        x_u = FeatureVector([-1, -1], position=lambda x: x.next_to(u_tex, LEFT))
        x_v = FeatureVector([-1, 1], position=lambda x: x.next_to(v_tex, RIGHT))
        x_u_vis = x_u.to_symbol_vis()
        x_v_vis = x_v.to_symbol_vis()
        formula = Tex(r"$\textrm{logit}(y_{u, v}) = \beta_0 + x_u^\top W x_v$")
        formula.shift(np.array([0, 3, 0]))
        w = WMatrix()
        w_vis = w.to_formal_vis()
        w_tex = Tex(r"$W$")
        w_tex.next_to(w_vis, DOWN)
        u_tex.next_to(x_u_vis, DOWN)
        x_v_vis.shift(np.array([-4, 3, 0])).rotate(PI / 2)
        v_tex.shift(np.array([-5.2, 3, 0]))
        formula.shift(np.array([0, -6.5, 0]))
        old_group = VGroup(w_vis, w_tex, u_tex, v_tex, x_u_vis, x_v_vis)
        old_group.scale(0.8)
        
        self.play(GrowFromCenter(old_group), Write(formula))
        self.wait(0.25)
        
        
        self.play(old_group.animate.shift(1.7 * LEFT))
        N_TOPIC = 3
        Q = Matrix([[r"Q_{%d, %d}" % (h, k) for k in range(N_TOPIC)] for h in range(N_FEAT)])
        Q.next_to(w_vis, 2.2 * RIGHT)
        Q_tex = Tex(r"\textrm{topic-group matrix} $Q$")
        Q_tex.next_to(Q, DOWN)
        
        topic_vector = Matrix([[r"t_{%d}" % i for i in range(N_TOPIC)]])
        topic_vector.next_to(Q, UP * 2)
        t_tex = Tex(r"\textrm{topic} $e_t$")
        t_tex.next_to(topic_vector, UP)
        new_group = VGroup(Q, Q_tex, topic_vector, t_tex)
        new_group.scale(0.8)
        
        formula_2 = Tex(r"$\textrm{logit}(y_{u, v}) = \beta_0 + x_u^\top W x_v + "
                        r"x_u^\top Q e_t + x_u^\top Q e_t $")
        formula_2.move_to(formula.get_center())
        
        self.play(GrowFromCenter(new_group), Transform(formula, formula_2))
        
        self.wait(3.5)
        self.play(*[FadeOut(mob)for mob in self.mobjects])

class MatrixImageScene(Scene):
    def construct(self):
        node_u = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        node_v = Circle(radius=0.125, fill_color=WHITE,
            fill_opacity=1, stroke_opacity=0, z_index=3)
        CENTER_L = np.array([-2.5, 0, 0])
        CENTER_R = np.array([2.5, 0, 0])
        node_u.shift(CENTER_L)
        node_v.shift(CENTER_R)
        u_tex = Tex("$x_u$")
        v_tex = Tex("$x_v$")
        u_tex.next_to(node_u, LEFT)
        v_tex.next_to(node_v, RIGHT)
        x_u = FeatureVector([-1, -1], position=lambda x: x.next_to(u_tex, LEFT))
        x_v = FeatureVector([-1, 1], position=lambda x: x.next_to(v_tex, RIGHT))
        x_u_vis = x_u.to_symbol_vis()
        x_v_vis = x_v.to_symbol_vis()
        formula = Tex(r"$\textrm{logit}(y_{u, v}) = \beta_0 + x_u^\top W x_v$")
        formula.shift(np.array([0, 3, 0]))
        w = WMatrix()
        w_vis = w.to_symbol_vis()
        w_tex = Tex(r"$W$")
        w_tex.next_to(w_vis, DOWN)
        u_tex.next_to(x_u_vis, DOWN)
        x_v_vis.shift(np.array([-4, 2.75, 0])).rotate(PI / 2)
        v_tex.shift(np.array([-5.2, 2.75, 0]))
        formula.shift(np.array([0, -6.5, 0]))
        old_group = VGroup(w_vis, w_tex, u_tex, v_tex, x_u_vis, x_v_vis)
        # old_group.scale(0.8)
        
        self.add(old_group, formula)
