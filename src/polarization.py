# from webconflib import * # pylint: disable=W0401,W0614
from network import MyExampleGraph, CENTER_L, CENTER_R

from manim import Scene, Line, Circle, Text, \
    Axes, Dot, DEGREES, ThreeDScene, LaggedStart, \
    Create, Uncreate, FadeOut, Transform, GrowFromCenter, \
    LEFT, RIGHT, DOWN, ShowPassingFlash, \
    GREEN, RED, BLUE, YELLOW, PURPLE, GOLD, TEAL

import numpy as np

CMAP = [
    (GREEN, GOLD),
    (TEAL, PURPLE),
]

class PolarizationPlotScene(Scene):
    def construct_plot_scene(self):
        axes = Axes(
            x_range=[1960, 2020, 20],
            y_range=[0, 8, 2],
        )
        regression_line = axes.plot(lambda x: -91.8 + 0.0475 * x, color=RED)

        x_min, x_max, x_step = 1960, 2020, 20
        y_min, y_max, y_step = 0, 8, 2
        
        dots = [Dot(point=axes.coords_to_point(x, y)) for x, y in [
            (1968, 1.7),
            (1973, 2.9),
            (1978, 2.2),
            (1980, 2),
            (1983, 2.7),
            (1990, 3),
            (1993, 1.8),
            (1998, 2.4),
            (2000, 2.8),
            (2004, 3.1),
            (2006, 3.2),
            (2010, 4.1),
            (2015, 3.7),
            (2020, 5.8),
        ]]
        
        axes = Axes(
            x_range=[x_min, x_max + x_step, x_step],
            y_range=[y_min, y_max + y_step, y_step],
            x_axis_config={
                "numbers_to_include": range(x_min, x_max + x_step, x_step),
                "decimal_number_config": {"group_with_commas": False, "num_decimal_places": 0},
            },
        )
        x_label = axes.get_x_axis_label("\\text{years}")
        y_label = axes.get_y_axis_label("\\text{Affective Polarization in U.S.}")
        ref = Text("(Garzia et al., 2023)", font_size=14).shift(3.4 * DOWN + 4.8 * RIGHT)
        self.play(Create(axes), Create(x_label), Create(y_label), Create(ref)) # Create(title),
        self.play(Create(regression_line), *[Create(dot) for dot in dots])
        self.wait(8)
    
    def construct(self):
        self.construct_plot_scene()
        self.play(*[FadeOut(mob)for mob in self.mobjects])


class GraphPolarizationScene(Scene):
    def construct_polarized_graph_scene(self, repetition=3, create_while=None, shift=np.zeros(3)):
        # corona = ImageMobject("assets/img/covid_19.png")
        # corona.scale(1.2)
        # corona.to_edge(RIGHT, buff=1)
        
        F = (np.random.random((30, 2)) < 0.5) * 2 - 1
        G = MyExampleGraph(N=30, F=F,
            homophily = {0: 1, 1: 1.5}, heterophily = {0: -2, 1: -10},
        )
        
        layout_1 = G.get_split_layout(0)
        layout = {node: pos + np.array([0, 0, 1.8 * F[node, 1]]) for node, pos in layout_1.items()}
        
        vis_g = G.to_manim(layout=layout_1, color_feature=0, vertex_cmap=CMAP[0]).shift(shift)
        circle_L_1 = Circle(radius=1.5, color=CMAP[0][0], stroke_width=8).shift(CENTER_L + shift)
        circle_R_1 = Circle(radius=1.5, color=CMAP[0][1], stroke_width=8).shift(CENTER_R + shift)
        objects_to_create = [circle_L_1, circle_R_1, vis_g]
        if create_while is not None:
            create_while(objects_to_create)
        else:
            self.play(*[Create(o) for o in objects_to_create])
        
        for _ in range(repetition):
            self.play(ShowPassingFlash(
                    G.to_manim(layout=layout_1, feature=0, highlight_edges=True).shift(shift),
                    run_time=2.5,
            ))
        
        # extra_shift = shift + np.array([0, 0, -2])
        # new_vis_G = G.to_manim(feature=1, color_feature=0, vertex_cmap=CMAP[0]).shift(extra_shift)
        # circle_L_2 = Circle(radius=1.5, color=CMAP[1][0], stroke_width=8).shift(
        #     CENTER_L + extra_shift)
        # circle_R_2 = Circle(radius=1.5, color=CMAP[1][1], stroke_width=8).shift(
        #     CENTER_R + extra_shift)
        # anims = [Transform(vis_g, new_vis_G), Create(circle_L_2), Create(circle_R_2),
        #     Uncreate(circle_L_1), Uncreate(circle_R_1)]
        # 
        new_vis_g = G.to_manim(layout=layout, color_feature=1, vertex_cmap=CMAP[1])
        new_flash = ShowPassingFlash(
                G.to_manim(layout=layout, feature=1, highlight_edges=True),
                run_time=2.5,
        )
        self.play(Transform(vis_g, 
            G.to_manim(layout=layout_1, color_feature=1, vertex_cmap=CMAP[1]).shift(shift)
        ), Uncreate(circle_L_1), Uncreate(circle_R_1))
        
        self.play(
            # self.camera._frame_center.animate.move_to(new_vis_G), 
            self.camera.phi_tracker.animate.set_value(-45. * DEGREES),
            Transform(vis_g, new_vis_g),
            GrowFromCenter(Line(LEFT * 4, RIGHT * 4).set_color(RED)),
            # *anims, 
            run_time=2
        )
        
        for _ in range(repetition):
            self.play(new_flash)#, vis_g.animate.shift(0.25 * UP))
        
        # circle_L = Circle(radius=1.5, color=CMAP[0][0], stroke_width=8).shift(CENTER_L + shift)
        # circle_R = Circle(radius=1.5, color=CMAP[0][1], stroke_width=8).shift(CENTER_R + shift)
        
        # self.wait(4)
        
        # circle_feat_1_L = Circle(radius=1.5, color=CMAP[1][0], stroke_width=8).shift(CENTER_L)
        # circle_feat_1_R = Circle(radius=1.5, color=CMAP[1][1], stroke_width=8).shift(CENTER_R)
    
    def construct(self):
        self.construct_polarized_graph_scene()
        self.play(*[FadeOut(mob)for mob in self.mobjects])
        

class PolarizationScene(PolarizationPlotScene, GraphPolarizationScene, ThreeDScene):
    def construct_polarization_scene(self):
        self.construct_plot_scene()
        self.wait(1.5)
        fade_out_plot = [FadeOut(mob) for mob in self.mobjects]
        
        self.construct_polarized_graph_scene(
            shift=np.array([0, 0, -3]),
            create_while=lambda objs: self.play(*([
                self.camera.phi_tracker.animate.set_value(180. * DEGREES),
                self.camera.theta_tracker.animate.set_value(-90. * DEGREES),
            ] + [
                LaggedStart(Create(o, run_time=4)) for o in objs
            ] + fade_out_plot
        ), run_time=4))
        
        self.play(*[FadeOut(mob)for mob in self.mobjects])
        
        # self.construct_polarized_graph_scene(shift=np.array([0, 0, -3]), create_while=lambda objs:
        #     self.move_camera(focal_distance=self.camera.focal_distance,
        #         theta=-90. * DEGREES,
        #         phi=180. * DEGREES,
        #         # frame_center=np.array([0, 0, 0]),
        #         added_anims=(fade_out_plot + [
        #             Create(o, rate_func=delay, run_time=8) for o in objs
        #         ]),
        #         run_time=4,
        #     )
        # )
        # self.construct_polarized_graph_scene(shift=np.array([0, 0, -3.5]))
        # self.play(*[FadeOut(mob)for mob in self.mobjects])
    
    def construct(self):
        self.construct_polarization_scene()


class FinaleScene(ThreeDScene):
    def construct_polarized_graph_scene(self, repetition=4, shift=np.zeros(3)):
        np.random.seed(123)
        F = np.sign(np.random.multivariate_normal([0, 0], [[1, 0.85], [0.85, 1]] , 30)).astype(int)
        assert np.all(F != 0)
        G = MyExampleGraph(N=30, F=F,
            homophily = {0: 1, 1: 1.5}, heterophily = {0: 5, 1: -10},
        )
        
        layout_1 = G.get_split_layout(0)
        layout = {node: pos + np.array([0, 0, 2.8 * F[node, 1]]) for node, pos in layout_1.items()}
        
        vis_g = G.to_manim(layout=layout_1, color_feature=0, vertex_cmap=[RED, BLUE]).shift(shift)
        circle_L_1 = Circle(radius=1.5, color=RED, stroke_width=8).shift(CENTER_L + shift)
        circle_R_1 = Circle(radius=1.5, color=BLUE, stroke_width=8).shift(CENTER_R + shift)
        objects_to_create = [circle_L_1, circle_R_1, vis_g]
        self.play(*[Create(o) for o in objects_to_create])
        
        for _ in range(4):
            self.play(ShowPassingFlash(
                    G.to_manim(layout=layout_1, feature=0, highlight_edges=True).shift(shift),
                    run_time=1,
            ))
        
        new_vis_g = G.to_manim(layout=layout, color_feature=1, vertex_cmap=[GREEN, YELLOW])
        new_flash = ShowPassingFlash(
                G.to_manim(layout=layout, feature=1, highlight_edges=True),
                run_time=2.5,
        )
        self.play(Transform(vis_g, 
            G.to_manim(layout=layout_1, color_feature=1, vertex_cmap=[GREEN, YELLOW]).shift(shift)
        ), Uncreate(circle_L_1), Uncreate(circle_R_1),
            # self.camera._frame_center.animate.move_to(new_vis_G), 
            self.camera.phi_tracker.animate.set_value(-45. * DEGREES),
            Transform(vis_g, new_vis_g),
            GrowFromCenter(Line(LEFT * 4, RIGHT * 4).set_color(RED)),
            # *anims, 
            run_time=2
        )
        
        for _ in range(repetition):
            self.play(new_flash, run_time=1.25)#, vis_g.animate.shift(0.25 * UP))
        
        # circle_L = Circle(radius=1.5, color=CMAP[0][0], stroke_width=8).shift(CENTER_L + shift)
        # circle_R = Circle(radius=1.5, color=CMAP[0][1], stroke_width=8).shift(CENTER_R + shift)
        
        # self.wait(4)
        
        # circle_feat_1_L = Circle(radius=1.5, color=CMAP[1][0], stroke_width=8).shift(CENTER_L)
        # circle_feat_1_R = Circle(radius=1.5, color=CMAP[1][1], stroke_width=8).shift(CENTER_R)
    
    def construct(self):
        self.construct_polarized_graph_scene()
        self.play(*[FadeOut(mob)for mob in self.mobjects], run_time=4)
