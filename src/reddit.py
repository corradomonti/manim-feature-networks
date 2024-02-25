# from lib import * # pylint: disable=W0401,W0614
from manim import VGroup, Scene, Line, Circle, Graph, \
    Create, FadeOut, Transform, GrowFromCenter, ApplyMethod, \
    Rectangle, Text, \
    RIGHT, UP, DEFAULT_STROKE_WIDTH, DOWN, LEFT, WHITE, BLACK

from collections import defaultdict
import itertools
import numpy as np

POSTS_FILL_WITH_STUFF = True


class Actor(VGroup):
    def __init__(self, label, shift, color=WHITE):
        self.c = Circle(radius=0.25, stroke_color=color, fill_color=BLACK, fill_opacity=1, z_index=3)
        self.c.shift(shift)
        if label:
            self.txt = Text(label)
            self.txt.next_to(self.c.get_corner(UP), UP)
            super().__init__(self.c, self.txt)
        else:
            super().__init__(self.c)
            
    def pos(self):
        return self.c.get_center()
        

def random_subintervals(l, char=0.25, sep_chance=0.05):
    a, b = 0, 0
    while b < l:
        b += char
        if b >= l or np.random.random() < sep_chance:
            yield (a, min(l, b))
            a, b = b + char, b + char

def fake_words(p1, p2, color):
    assert p1[1] == p2[1]
    y = p1[1]
    x1 = p1[0]
    x2 = p2[0]
    
    for a, b in random_subintervals(x2 - x1):
        yield Line(
            np.array([x1 + a, y, 0]),
            np.array([x1 + b, y, 0]),
            color=color)
    
    
class Post(VGroup):
    def __init__(self, label, y, indent=0, color=WHITE):
        pos = np.array([-2. + indent * 1, y, 0])
        self.label = label
        self.u = Actor(label, pos + DOWN, color=color)
        
        self.r = Rectangle(height=1., width=5, color=color)
        self.r.next_to(self.u.get_corner(DOWN + RIGHT), 2 * RIGHT + UP)
        self.r.shift(DOWN * 0.25)
                   
        self.words = []
        if POSTS_FILL_WITH_STUFF:
            for d in (-0.16, 0.1):#-.05, 0.45):
                pos_start = self.r.get_corner(LEFT) + .5 * RIGHT + d * UP
                pos_end = self.r.get_corner(RIGHT) + .5 * LEFT + d * UP
                self.words += list(fake_words(pos_start, pos_end, color=color))
        
        if indent == 0:
            news_text = Text("[news]")
            news_text.next_to(self.u.c, 2 * LEFT)
            news_texts = [news_text]
        else:
            news_texts = []
                
        super().__init__(self.u, self.r, *self.words, *news_texts)
    
    def except_nodes(self):
        return VGroup(self.r, self.u.txt, *self.words)

            
class RedditScene(Scene):
    def construct_reddit_scene(self, colors=None, repetition=4):
        if colors is None:
            colors = [WHITE]
        np.random.seed(12345)
        
        # Submissions: ABBBCCDDDDDEEEEE
        #              0123456789012345678
        labels =      "abcdbaefghiabcdefgh"
        edges = [(2, 1), (3, 1), (5, 4), (7, 6), (8, 7), (9, 6), (10, 9), 
                 (12, 11), (13, 12), (14, 11), (15, 14), (17, 16), (18, 17)]
        post2indent = defaultdict(int)
        for u, v in edges:
            post2indent[u] = post2indent[v] + 1
        
        posts = []
        post_y = 6
        for label, color, i in zip(
            itertools.cycle(labels),
            itertools.cycle(colors),
            range(len(labels))
        ):
            if post2indent[i] == 0:
                post_y -= 2.75
            else:
                post_y -= 1.75
            posts.append(Post(label, post_y, indent=post2indent[i], color=color))
            
        self.play(*[GrowFromCenter(p) for p in posts])
        self.wait(.5)
        
        AVG_Y_SHIFT = 3.5
        for _ in range(repetition):
            y_shift = (np.random.random() * 0.5 + .75) * AVG_Y_SHIFT * UP
            plays = [ApplyMethod(p.shift, y_shift) for p in posts]
            self.play(*plays)
            self.wait(.5)
            
        # edges_vis = []
        # edges_anim = []
        # for u, v in edges:
        #     edge_vis = Line(posts[u].u.pos(), posts[v].u.pos(), z_index=-1)
        #     edges_vis += [edge_vis]
        #     edges_anim += [GrowFromPoint(edge_vis, posts[u].u.pos())]
        # 
        # self.play(*([FadeOut(p.except_nodes()) for p in posts] + edges_anim))
        # nodes = [p.u.c for p in posts]
        # return nodes, edges_vis
        
        graph = Graph(list(range(len(posts))), edges,
            layout={i: post.u.c.get_center() for i, post in enumerate(posts)},
            layout_scale=5,
            edge_config={
                'stroke_opacity': 0.5,
                'stroke_width': 0.25 * DEFAULT_STROKE_WIDTH,
                'stroke_color': '#999999'
            },
            vertex_config={"fill_color": WHITE, "radius": 0.125},
        )
        self.play(*(
            [Transform(post.u.c, graph[i]) for i, post in enumerate(posts)] +
            [FadeOut(p) for p in posts] +
            [Create(graph)]
        ))
        
        return graph
        
    
    def construct(self):
        self.construct_reddit_scene()
        self.play(*[FadeOut(mob)for mob in self.mobjects])
        
