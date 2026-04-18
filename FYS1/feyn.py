from manim import *
import numpy as np

class FeynmanDiagram(Scene):

    # ---------- Arrow ----------
    def arrow_mid_segment(self, p_start, p_end, size=0.2, color=BLUE):
        mid = (p_start + p_end) / 2
        vec = p_end - p_start
        angle = np.arctan2(vec[1], vec[0])

        p1 = np.array([0, 0, 0])
        p2 = np.array([-size, size, 0])
        p3 = np.array([-size, -size, 0])

        arrow = VGroup(
            Line(p2, p1, color=color),
            Line(p1, p3, color=color)
        )

        arrow.move_to(mid)
        arrow.rotate(angle)
        return arrow

    # ---------- Fermion from path ----------
    def make_fermion_path(self, points, color=BLUE):
        path = VMobject(color=color)
        path.set_points_as_corners(points)  # continuous path

        arrows = VGroup()

        # Add arrows per segment
        for i in range(len(points) - 1):
            arrow = self.arrow_mid_segment(points[i], points[i+1], color=color)
            arrows.add(arrow)

        return VGroup(path, arrows)

    # ---------- Photon ----------
    def make_photon(self, start, end, amplitude=0.2, freq=10):
        def path(t):
            vec = end - start
            perp = np.array([-vec[1], vec[0], 0])
            perp = perp / np.linalg.norm(perp)
            return start + vec*t + amplitude*np.sin(freq*np.pi*t)*perp

        return ParametricFunction(path, t_range=[0,1], color=YELLOW)

    # ---------- Scene ----------
    def construct(self):

        # --- Key points (vertices etc.) ---
        p = {
            "in1": LEFT*4 + UP*1.5,
            "in2": LEFT*4 + DOWN*1.5,
            "v1": UP*1,
            "v2": DOWN*1,
            "out1": RIGHT*4 + UP*1.5,
            "out2": RIGHT*4 + DOWN*1.5,
        }

        # --- Fermions as paths ---
        fermion_paths = [
            [p["in1"], p["v1"], p["out1"]],  # electron line
            [p["in2"], p["v2"], p["out2"]],  # muon line
            [p["in1"] + UP*0.5, p["v1"] + UP*0.5, p["out1"] + UP*0.5],  # extra line
        ]

        fermion_paths_mobjects = [
            self.make_fermion_path(path)
            for path in fermion_paths
        ]

        # Split paths and arrows
        paths = VGroup(*[fp[0] for fp in fermion_paths_mobjects])
        arrows = VGroup(*[fp[1] for fp in fermion_paths_mobjects])

        # --- Photon ---
        photon = self.make_photon(p["v1"], p["v2"])

        # --- Vertices ---
        vertices = VGroup(
            Dot(p["v1"], color=RED),
            Dot(p["v2"], color=RED)
        )
        vertices.set_z_index(10)

        # --- Labels ---
        labels = VGroup(
            MathTex("e^-").next_to(p["in1"], LEFT),
            MathTex("\\mu^-").next_to(p["in2"], LEFT),
            MathTex("e^-").next_to(p["out1"], RIGHT),
            MathTex("\\mu^-").next_to(p["out2"], RIGHT),
            MathTex("\\gamma").next_to(photon, RIGHT)
        )

        # --- Animation ---
        self.play(*[Create(f) for f in paths])    # smooth continuous drawing
        self.play(*[Create(f) for f in arrows])
        self.play(*[Create(v) for v in vertices])
        self.play(Create(photon))
        self.play(Write(l) for l in labels)

        self.wait(5)